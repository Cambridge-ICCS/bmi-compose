import numpy as np
from numpy.typing import NDArray
from typing import Any
from bmipy import Bmi
from pathlib import Path
from enum import Enum
import pathlib
from decimal import Decimal, getcontext

class CouplingType(Enum):
  ONE_WAY = 1
  TWO_WAY = 2
  


## the idea here is that the interface list passed to the compose function would be in a specified order, so interface[0] is a dictionary with units that
## the user wishes to set during the update, interface[1] could be conversions but I think this may just need to be hard coded by the user outside of the update
## as in the gipl example the conversion is not done shared variables but rather 2 diff`erent ones.

def compose(bmi1 : Bmi, bmi2 : Bmi, coupling_type : CouplingType = CouplingType.ONE_WAY, unitsDict : dict = None, conversions : list[tuple[dict, str, Any]] = None) -> Bmi:

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

  Returns
   -------
  composed_bmi : Bmi
   The composed BMI model.
  """


  fwdInterfaceVars = intersection(bmi1.get_output_var_names(), bmi2.get_input_var_names())

  if coupling_type == CouplingType.TWO_WAY:
    bwdInterfaceVars = intersection(bmi1.get_input_var_names(), bmi2.get_output_var_names())
    
  getcontext().prec = 28
  bmi_cycles = {"bmi1_cycles" : 1, "bmi2_cycles" :  1}
  
  time_step = {"max_time_step"  : float(0)}

  assert bmi1.bmi.get_time_units() == bmi2.bmi.get_time_units(), "These BMIs do not share the same time step units" 

  timeUnits = bmi1.bmi.get_time_units()

  assert bmi1.bmi.get_start_time() == bmi2.bmi.get_start_time(), "These BMI's do not start at the same timestep"

  class ComposedBmi(Bmi):


    def setup(self, *args, **kwargs):
      
      if ("setup" in dir(bmi1) and "setup" in dir(bmi2)):
        defaults1 = bmi1.setup(*args, **kwargs)
        defaults2 = bmi2.setup(*args, **kwargs)

        path1 = pathlib.Path(defaults1[1],defaults1[0])
        path2 = pathlib.Path(defaults2[1],defaults2[0])

        
        defaults = composeConfig(path1, path2)


        return defaults
      
      else:
        raise FileNotFoundError("One of the selected BMI's does not have a setup method.")


    def initialize(self, dir:list[str] = ["."]):


      
        
      conf1, conf2 = splitConf(dir[0])
      


      bmi1.initialize(*conf1)
      bmi2.initialize(*conf2)


      bmi1TimeStep = Decimal(str(bmi1.bmi.get_time_step()))
      bmi2TimeStep = Decimal(str(bmi2.bmi.get_time_step()))

      if bmi1TimeStep % bmi2TimeStep == 0:
        bmi_cycles["bmi2_cycles"] = int(bmi1TimeStep / bmi2TimeStep)
        time_step["max_time_step"] = bmi1.bmi.get_time_step()

      elif bmi2TimeStep % bmi1TimeStep == 0:
        bmi_cycles["bmi1_cycles"] = int(bmi2TimeStep / bmi1TimeStep)
        time_step["max_time_step"] = bmi2.bmi.get_time_step()

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


      for i in range(0, bmi_cycles["bmi1_cycles"]):
        bmi1.update()

      if unitsDict != None:

        for key, value in unitsDict.items():
          bmi2.set_value(key, bmi1.get_value(key, units=value))
          fwdVarsCopy.remove(key)
      
      if conversions != None:
        
        for i in conversions:
          conversionVars = []
          
          for key, value in i[0].items():
           
            varNames = bmi1.get_value(key, units = value)
            conversionVars.append(varNames)

          setConv = i[2](*conversionVars)
          
          bmi2.set_value(i[1], setConv) 
          


      for i in fwdVarsCopy:
        
        bmi2.set_value(i, bmi1.get_value(i))

      for i in range(0, bmi_cycles["bmi2_cycles"]):
        bmi2.update()
      

      if coupling_type == CouplingType.TWO_WAY:
        bwdVarsCopy = bwdInterfaceVars.copy()
        
        if unitsDict != None:
          for key, value in unitsDict.items():
            bmi1.set_value(key, bmi2.get_value(key, units=value))
            bwdVarsCopy.remove(key)


        for i in bwdVarsCopy:
          bmi1.set_value(i, bmi2.get_value(i))

      return self
    
    def get_value(self, name : str, out=None, units=None, angle=None, at=None, method=None):


      
      if name in union(bmi1.get_input_var_names(),bmi1.get_output_var_names()):
        return  bmi1.get_value(name, out, units, angle, at, method)

      
      elif name in union(bmi2.get_input_var_names(),bmi2.get_output_var_names()):
        return bmi2.get_value(name, out, units, angle, at, method)

    def set_value(self, name : str, value : int):

     
      
      if name in fwdInterfaceVars:
        bmi1.set_value(name,value)
        bmi2.set_value(name,value)
      
      elif name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        bmi1.set_value(name, value)

      elif name in union(bmi2.get_input_var_names(), bmi2.get_output_var_names()):
        bmi2.set_value(name,value)

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
      return union(bmi1.bmi.get_input_var_names(), bmi2.bmi.get_input_var_names())

    def get_output_var_names(self):
      return union(bmi1.bmi.get_outpu_var_names(), bmi2.bmi.get_output_var_names())

    def get_current_time(self):
      return bmi1.bmi.get_current_time()

    def get_start_time(self):
      return bmi1.bmi.get_start_time()

    def get_end_time(self):
      if bmi1.bmi.get_end_time() == bmi2.bmi.get_end_time():
        return bmi1.get_end_time()
      else:
        return min(bmi1.bmi.get_end_time(), bmi2.bmi.get_end_time())

    def get_time_step(self):
      return  time_step["max_time_step"]


    def get_time_units(self):
      return timeUnits

    def set_value_at_indices(self, name :str, index : int, value : NDArray[Any]):
      
      if name in fwdInterfaceVars:
        bmi1.bmi.set_value_at_indices(name, index, value)
        bmi2.bmi.set_value_at_indices(name, index, value)
      
      elif name in union(bmi1.get_input_var_names(), bmi1.get_output_var_names()):
        bmi1.bmi.set_value_at_indices(name, index, value)

      elif name in union(bmi2.get_input_var_names(), bmi2.get_output_var_names()):
        bmi2.bmi.set_value_at_indices(name, index, value)

    def get_value_at_indices(self, name : str, index : int):
      
      if name in union(bmi1.get_input_var_names(),bmi1.get_output_var_names()):
        return  bmi1.bmi.get_value_at_indices(name, index)

      
      elif name in union(bmi2.get_input_var_names(),bmi2.get_output_var_names()):
        return bmi2.bmi.get_value_at_indices(name, index)
      

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
  
    def get_var_grid(self):
      raise NotImplemented("Not implemented")

    def get_grid_type(self):
      raise NotImplemented("Not implemented")

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


    ## when running the models none of them seem to have these two methods even when run as gipl.bmi.get_input_item count() for some reason
    def get_input_item_count(self):
      return bmi1.bmi.get_input_item_count() + bmi2.bmi.get_input_item_count()

    def get_output_item_count(self):
      return bmi1.bmi.get_output_item_count() + bmi2.bmi.get_output_item_count()
    

  return ComposedBmi()



#helpers

def union(xs, ys):
  return (xs + tuple([y for y in ys if y not in xs]))

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
