import numpy as np
from numpy.typing import NDArray
from typing import Any
import os
from bmipy import Bmi
from pathlib import Path
from enum import Enum
from decimal import Decimal, getcontext

class CouplingType(Enum):
  ONE_WAY = 1
  TWO_WAY = 2


## the idea here is that the interface list passed to the compose function would be in a specified order, so interface[0] is a dictionary with units that
## the user wishes to set during the update, interface[1] could be conversions but I think this may just need to be hard coded by the user outside of the update
## as in the gipl example the conversion is not done shared variables but rather 2 diff`erent ones.

def compose(bmi1 : Bmi, bmi2 : Bmi, coupling_type : CouplingType = CouplingType.TWO_WAY, unitsDict : dict = None, conversions : list[tuple[dict, str, Any]] = None) -> Bmi:

  """Composes two BMI fitted models into a singular BMI model.

  Parameters
  ----------
  bmi1 : Bmi
    First Bmi model to be composed.
  bmi2 : Bmi
    Second Bmi model to be composed.
  coupling_type : Enum
    Dictates if the coupling should be one way or two way.
  unitsDict : dict
    Dictionary of units you wish to set during update.
  conersions : list[tuple(dict,str,Any)]
    list of conversions you wish to perform during the update phase of the bmi.
      dict : key = get variable, value = units
      str = set variable
      Any = lambda function to be used on get variables to then be set
  Returns
   -------
  composed_bmi : Bmi
   The composed BMI model.
  """
  # Get the intersection of the composable interface
  fwdInterfaceVars = intersection(bmi1.get_output_var_names(), bmi2.get_input_var_names())

  # In the case of the two way coupling, calculate back interface
  if coupling_type == CouplingType.TWO_WAY:
    bwdInterfaceVars = intersection(bmi1.get_input_var_names(), bmi2.get_output_var_names())

  # TODO: consider making this a parameter
  getcontext().prec = 28
  # Sub-model cycles per composed model cycle
  bmi_cycles = {"bmi1_cycles" : 1, "bmi2_cycles" :  1}

  max_time_step = float(0)

  # Start times must align
  assert bmi1.get_start_time() == bmi2.get_start_time(), "These BMI's do not start at the same timestep"

  # Build the composed model internally
  class ComposedBmi(Bmi):

    def initialize(self, config_file:str):
      nonlocal max_time_step
      if not isinstance(config_file, (str, os.PathLike)):
        raise TypeError("config_file must be a merged config path string")

      conf1, conf2 = splitConf(config_file)
      conf1_path = str(Path(conf1[1], conf1[0]))
      conf2_path = str(Path(conf2[1], conf2[0]))

      # Prefer BMI-style initialize(config_path), but keep tuple fallback for
      # wrappers that expect (filename, directory).
      try:
        bmi1.initialize(conf1_path)
      except TypeError:
        bmi1.initialize(*conf1)

      try:
        bmi2.initialize(conf2_path)
      except TypeError:
        bmi2.initialize(*conf2)

      assert bmi1.get_time_units() == bmi2.get_time_units(), "These BMIs do not share the same time step units"

      bmi1TimeStep = Decimal(str(bmi1.get_time_step()))
      bmi2TimeStep = Decimal(str(bmi2.get_time_step()))

      if bmi1TimeStep % bmi2TimeStep == 0:
        bmi_cycles["bmi2_cycles"] = int(bmi1TimeStep / bmi2TimeStep)
        max_time_step = bmi1.get_time_step()

      elif bmi2TimeStep % bmi1TimeStep == 0:
        bmi_cycles["bmi1_cycles"] = int(bmi2TimeStep / bmi1TimeStep)
        max_time_step = bmi2.get_time_step()

      else:
        raise ValueError("Time steps are incompatible (one is not a factor of the other): dt1 = " + str(bmi1.time_step) + " and dt2 = " + str(bmi2.time_step))

      return self

    def update(self):
      """Update the first Bmi, sets the shared variables of the second Bmi and then updates the second BMI.
      If coupling_type is TWO_WAY will do as above but after Bmi 2 is updated the shared variables will be
      set for the first Bmi and then the first Bmi will be updated.
      """

      fwdVarsCopy = fwdInterfaceVars.copy()

      assert bmi_cycles["bmi1_cycles"] == 1 or bmi_cycles["bmi2_cycles"] == 1

      # Cycle the first model 
      for i in range(0, bmi_cycles["bmi1_cycles"]):
        bmi1.update()

      # If we have a units conversion
      # TODO: consider
      # if unitsDict != None:
      #   for key, value in unitsDict.items():
      #     bmi2.set_value(key, bmi1.get_value(key, units=value))
      #     fwdVarsCopy.remove(key)

      # TODO: fix things here.
      # if conversions != None:
      #   for i in conversions:
      #     conversionVars = []

      #     for key, value in i[0].items():
      #       varNames = bmi1.get_value(key, units = value)
      #       conversionVars.append(varNames)

      #     setConv = i[2](*conversionVars)

      #     bmi2.set_value(i[1], setConv)

      # Transfer variables from the first model to the second
      for i in fwdVarsCopy:
        out = np.empty(1)
        bmi1.get_value(i, out)
        bmi2.set_value(i, out)
    
      for i in range(0, bmi_cycles["bmi2_cycles"]):
        bmi2.update()

      # TODO: write a test that checks the time is now consistent.
      

      if coupling_type == CouplingType.TWO_WAY:
        bwdVarsCopy = bwdInterfaceVars.copy()

        # TODO: check
        # if unitsDict != None:
        #   for key, value in unitsDict.items():
        #     bmi1.set_value(key, bmi2.get_value(key, units=value))
        #     bwdVarsCopy.remove(key)

        # if conversions != None:

        #   for i in conversions:
        #     conversionVars = []

        #     for key, value in i[0].items():

        #       varNames = bmi2.get_value(key, units = value)
        #       conversionVars.append(varNames)

        #     setConv = i[2](*conversionVars)

        #     bmi1.set_value(i[1], setConv)


        for i in bwdVarsCopy:
          out = np.empty(1)
          bmi2.get_value(i, out)
          bmi1.set_value(i, out)

      return self

    def get_value(self, name : str, dest : NDArray[Any]) -> NDArray[Any]:
      # Note that if a name is in both models then the value
      # should be the same between the two
      if name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        return bmi1.get_value(name, dest)

      elif name in union(bmi2.get_input_var_names(), bmi2.get_output_var_names()):
        return bmi2.get_value(name, dest)
      
      raise KeyError(f"Variable name '{name}' not found in the model.")

    def set_value(self, name: str, src: NDArray[Any]) -> None:
      if name in bmi1.get_input_var_names():
        bmi1.set_value(name, src)

      if name in bmi2.get_input_var_names():
        bmi2.set_value(name, src)

      if name not in bmi1.get_input_var_names() and name not in bmi2.get_input_var_names():
          raise KeyError(f"Variable name '{name}' not found in the model.")
      else:
          return None

    def get_component_name(self):
      """Get the component name."""
      if coupling_type == CouplingType.TWO_WAY:
        return (bmi1.get_component_name() + " <-> " + bmi2.get_component_name())
      else:
        return (bmi1.get_component_name() + " -> " + bmi2.get_component_name())

    def finalize(self):
      bmi1.finalize()
      bmi2.finalize()
      return self

    def update_until(self,time):
      """ Updates the first Bmi until a given type, sets shared variables of the second Bmi and then updates the second Bmi.
      If coupling_type is TWO_WAY does as above but then also sets shared variables for the first Bmi and updates the first Bmi.
      """
      fwdVarsCopy = fwdInterfaceVars.copy()

      if coupling_type == CouplingType.TWO_WAY:

        bwdVarsCopy = bwdInterfaceVars.copy()

        bmi1.update_until(time)

        if unitsDict != None:
          for key, value in unitsDict.items():
            bmi1.set_value(key, bmi2.get_value(key, units=value))
            fwdVarsCopy.remove(key)

        for i in fwdVarsCopy:

          bmi2.set_value(i, bmi1.get_value(i))

        bmi2.update_until(time)

        if unitsDict != None:

          for key, value in unitsDict.items():
            bmi1.set_value(key, bmi2.get_value(key, units=value))
            bwdVarsCopy.remove(key)

        bmi1.update_until(time)

      else:
        bmi1.update_until(time)

        if unitsDict != None:

          for key, value in unitsDict.items():
            bmi1.set_value(key, bmi2.get_value(key, units=value))
            fwdVarsCopy.remove(key)

        for i in fwdVarsCopy:

          bmi2.set_value(i, bmi1.get_value(i))

        bmi2.update_until(time)

      return self




    def get_input_var_names(self):
      return union(bmi1.get_input_var_names(), bmi2.get_input_var_names())

    def get_output_var_names(self):
      return union(bmi1.get_output_var_names(), bmi2.get_output_var_names())

    def get_current_time(self):
      return bmi1.get_current_time()

    def get_start_time(self):
      return bmi1.get_start_time()

    def get_end_time(self):
      if bmi1.get_end_time() == bmi2.get_end_time():
        return bmi1.get_end_time()
      else:
        return min(bmi1.get_end_time(), bmi2.get_end_time())

    def get_time_step(self):
      return  max_time_step


    def get_time_units(self):
      return bmi1.get_time_units()


    def set_value_at_indices(self, name :str, index : NDArray[Any], value : NDArray[Any]):

      if name in fwdInterfaceVars:
        bmi1.set_value_at_indices(name, index, value)
        bmi2.set_value_at_indices(name, index, value)

      elif name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        bmi1.set_value_at_indices(name, index, value)

      elif name in union(bmi2.get_input_var_names(), bmi2.get_output_var_names()):
        bmi2.set_value_at_indices(name, index, value)

    def get_value_at_indices(self, name : str, dest: NDArray[Any], inds: NDArray[Any]):

      if name in union(bmi1.get_input_var_names(),bmi1.get_output_var_names()):
        return  bmi1.get_value_at_indices(name, dest, inds)

      elif name in union(bmi2.get_input_var_names(),bmi2.get_output_var_names()):
        return bmi2.get_value_at_indices(name, dest, inds)


    def get_value_ptr(self, name):
      if name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        return bmi1.get_value_ptr(name)
      else:
        return bmi2.get_value_ptr(name)

    def get_var_location(self, name):

      if name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        return bmi1.get_var_location(name)
      else:
        return bmi2.get_var_location(name)

    def get_var_nbytes(self,name):

      if name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        return bmi1.get_var_nbytes(name)
      else:
        return bmi2.get_var_nbytes(name)

    def get_var_type(self,name):
      if name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        return bmi1.get_var_type(name)
      else:
        return bmi2.get_var_type(name)

    def get_var_units(self, name : str ):
      if name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        return bmi1.get_var_units(name)
      else:
        return bmi2.get_var_units(name)

    def get_var_itemsize(self,name):
      if name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        return bmi1.get_var_itemsize(name)
      else:
        return bmi2.get_var_itemsize(name)

    def get_var_grid(self, name):
      # TODO: sort out what to do if the grid ids are difference.
      if name in fwdInterfaceVars:
        assert bmi1.get_var_grid(name) == bmi2.get_var_grid(name), "These BMIs do not share the same ID for the same variable grid"
        return bmi1.get_var_grid(name)

      elif name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        return bmi1.get_var_grid(name)

      else:
        return bmi2.get_var_grid(name)

    def get_grid_type(self, grid_id):
      assert bmi1.get_grid_type(grid_id) == bmi2.get_grid_type(grid_id), "These BMIs have different types for the same variable grid"
      return bmi1.get_grid_type(grid_id)


    def get_grid_edge_count(self):
      raise NotImplemented("Not implemented")

    def get_grid_edge_nodes(self):
      raise NotImplemented("Not implemented")

    def get_grid_face_count(self):
      raise NotImplemented("Not implemented")

    def get_grid_face_edges(self):
      raise NotImplemented("Not implemented")

    def get_grid_face_nodes(self):
      raise NotImplemented("Not implemented")

    def get_grid_node_count(self):
      raise NotImplemented("Not implemented")

    def get_grid_nodes_per_face(self):
      raise NotImplemented("Not implemented")

    def get_grid_origin(self):
      raise NotImplemented("Not implemented")

    def get_grid_rank(self):
      raise NotImplemented("Not implemented")

    def get_grid_size(self):
      raise NotImplemented("Not implemented")

    def get_grid_spacing(self):
      raise NotImplemented("Not implemented")

    def get_grid_shape(self):
      raise NotImplemented("Not implemented")

    def get_grid_x(self):
      raise NotImplemented("Not implemented")

    def get_grid_y(self):
      raise NotImplemented("Not implemented")

    def get_grid_z(self):
      raise NotImplemented("Not implemented")


    ## when running the models none of them seem to have these two methods even when run as gipl.get_input_item count() for some reason
    def get_input_item_count(self):
      return bmi1.get_input_item_count() + bmi2.get_input_item_count()

    def get_output_item_count(self):
      return bmi1.get_output_item_count() + bmi2.get_output_item_count()


  return ComposedBmi()



#helpers

def union(xs, ys):
  return (list(xs) + list([y for y in ys if y not in xs]))

def intersection(x,y):
  return [i for i in x if i in y]

def composeConfig(config1:str, config2:str, suffix:str = ".txt"):
  """Merges two config fiels into a single one
  """

  with open(config1, "r") as c1:
    conf1 = c1.read()

  with open(config2, "r") as c2:
    conf2 = c2.read()

  ## sets a marker for where the first config file ends and the second one starts
  content = conf1 + "\n\nStart of config file 2: \n\n" + conf2

  ## set the correct suffix if the config file is of cfg format
  confName = "mergedConf"+suffix

  with open(confName, "w") as merge:
    merge.write(content)

  confPath = Path(confName)

  composeConf = (str(confPath), str(confPath.parent))

  return composeConf

## splits a merged config file and returns the file path and absolute file path of the 2 new split files
def splitConf(config_path):
  with open(config_path, "r") as split:
    test = split.read()
    splitConf = str(test).split("Start of config file 2: \n\n")

    bmi1conf = splitConf[0]
    bmi2conf = splitConf[1]

    if ".cfg" in config_path:
      with open("bmi1Conf.cfg", "w") as bmi_1:
        bmi_1.write(bmi1conf)

      with open("bmi2Conf.cfg", "w") as bmi_2:
        bmi_2.write(bmi2conf)

      confPath1 = Path("bmi1Conf.cfg")
      confPath2 = Path("bmi2Conf.cfg")

    else:
      with open("bmi1Conf.txt", "w") as bmi_1:
        bmi_1.write(bmi1conf)

      with open("bmi2Conf.txt", "w") as bmi_2:
        bmi_2.write(bmi2conf)

      confPath1 = Path("bmi1Conf.txt")
      confPath2 = Path("bmi2Conf.txt")

    conf1 = (str(confPath1), str(confPath1.parent))
    conf2 = (str(confPath2), str(confPath2.parent))

  return conf1, conf2