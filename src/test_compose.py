import numpy as np
from numpy.typing import NDArray
from typing import Any
from bmipy import Bmi
from pathlib import Path




def compose(bmi1 : Bmi, bmi2 : Bmi, interface: list[str] = []) -> Bmi:

  interfaceVars = intersection(bmi1.get_output_var_names(), bmi2.get_input_var_names())

  composedInputs = union(bmi1.get_input_var_names(), bmi2.get_input_var_names())

  
  class ComposedBmi(Bmi):

    def setup(self, *args, **kwargs):
      
      defaults1 = bmi1.setup(*args, **kwargs)
      defaults2 = bmi2.setup(*args, **kwargs)

      print(defaults1)
      
      defaults = composeConfig(defaults1[1] + "/" + defaults1[0], defaults2[1] + "/" + defaults2[0])


      return defaults


    def initialize(self, config_file :str):
        
      conf1, conf2 = splitConf(config_file[0])
      


      bmi1.initialize(*conf1)
      bmi2.initialize(*conf2)
      return self

    def update(self):
      # At most one model with have multiple cycles run
      bmi1.update()

      for i in interfaceVars:
        
        bmi2.set_value(i, bmi1.get_value(i))

      bmi2.update()

      return self
    
    def get_value(self, name : str, dest: NDArray[Any] = None):


      
      if name in bmi1.get_input_var_names():
        out = bmi1.get_value(name,dest)
      

      elif name in interfaceVars:
        out = bmi1.get_value(name,dest)

      
      elif name in bmi2.get_output_var_names():
        out = bmi2.get_value(name,dest)
      
      return out



    def set_value(self, name : str, value : int):

      if name in bmi1.get_input_var_names():
        bmi1.set_value(name, value)
      
      elif name in interfaceVars:
        bmi1.set_value(name,value)
        bmi2.set_value(name,value)
      
      elif name in bmi2.get_output_var_names():
        bmi2.set_value(name,value)

      return self
        
    


    def get_component_name(self):
      return self.name


    def finalize(self):
      raise NotImplemented("Not implemented")

    def update_until(self):
      raise NotImplemented("Not implemented")

    def get_input_var_names(self):
      return composedInputs

    def get_output_var_names(self):
      return []

    def get_current_time(self):
      raise NotImplemented("Not implemented")

    def get_start_time(self):
      raise NotImplemented("Not implemented")

    def get_end_time(self):
      raise NotImplemented("Not implemented")

    def get_time_step(self):
      return 0.1

    def get_time_units(self):
      raise NotImplemented("Not implemented")


    def set_value_at_indices(self):
      raise NotImplemented("Not implemented")

    def get_value_at_indices(self):
      raise NotImplemented("Not implemented")

    def get_value_ptr(self):
      raise NotImplemented("Not implemented")

    def get_var_location(self):
      raise NotImplemented("Not implemented")

    def get_var_nbytes(self):
      raise NotImplemented("Not implemented")

    def get_var_type(self):
      raise NotImplemented("Not implemented")

    def get_var_units(self):
      raise NotImplemented("Not implemented")

    def get_var_itemsize(self):
      raise NotImplemented("Not implemented")

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

    def get_input_item_count(self):
      raise NotImplemented("Not implemented")

    def get_output_item_count(self):
      raise NotImplemented("Not implemented")
    

  return ComposedBmi()



#helpers

def union(xs, ys):
  return (xs + tuple([y for y in ys if y not in xs]))

def intersection(x,y):
  return [i for i in x if i in y]


def composeConfig(config1:str, config2:str):

  with open(config1, "r") as c1:
    conf1 = c1.read()

  with open(config2, "r") as c2:
    conf2 = c2.read()

  content = conf1 + " ? " + conf2
  
  
  
  if ".cfg" in config1:

    with open("mergedConf.cfg", "w") as merge:
      merge.write(content)

    confPath = Path("mergedConf.cfg")

    composeConf = (str(confPath), str(confPath.parent))

  else:


    with open("mergedConf.txt", "w") as merge:
      merge.write(content)

    confPath = Path("mergedConf.txt")

    composeConf = (str(confPath), str(confPath.parent))

  return composeConf




## splits a merged config file and returns the file path and absolute file path of the 2 new split files
def splitConf(config_path):
  with open(config_path, "r") as split:
    test = split.read()
    splitConf = str(test).split("?")

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
