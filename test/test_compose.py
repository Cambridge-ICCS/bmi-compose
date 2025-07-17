import pymt.models
import numpy as np
from bmipy import Bmi

cem = pymt.models.Cem
waves = pymt.models.Waves

def cemtest(bmi1 : Bmi, bmi2 : Bmi) -> Bmi:


  
  class ComposedBmi(Bmi):

    def setup(self, args1 = {}, args2 = {}):
      
      cem_defaults = bmi1.setup(**args1)
      waves_defaults = bmi2.setup(**args2)

      return self, cem_defaults, waves_defaults


    def initialize(self, config_file1 : str, config_file2 : str):
        bmi1.initialize(*config_file1)
        bmi2.initialize(*config_file2)
        return self

    def update(self, set_dict : dict):
      # At most one model with have multiple cycles run
      bmi1.update()


      # Want to be able to pass a dictionary which specifies which variables to get from BMI1 in order
      # to set thenm for BMI2. We check if they are the same else we have to distinguish between the different variable names.
      # on the CEM example notebook they set a variable for BMI2 using an array created outside of BMI and teh update process,
      # so we need to chack if an argument of a different type is passed through the dictionary or not.
      for key,value in set_dict.items():
        
        if type(value) is not str:
          bmi2.set_value(key, value)
        
        else:
          bmi2.set_value(key, bmi1.get_value(value))

      bmi2.update()

      return self
    
    def get_value(self, var_name : str, output : str = '', which_Bmi = 0):

      if which_Bmi == 1:
        bmi = bmi1
      
      else:
        bmi = bmi2

      if output == '':
        return bmi.get_value(var_name)
      
      else:
        return bmi.get_value(var_name, out = output)
      

    def set_value(self, which_Bmi, set_vals : dict):

      if which_Bmi == 0:
        bmi = bmi1

      elif which_Bmi == 1:
        bmi = bmi2

      for key,value in set_vals.items():
        bmi.set_value(key,value)

      return self
        
    


    def get_component_name(self):
      return self.name


    def finalize(self):
      raise NotImplemented("Not implemented")

    def update_until(self):
      raise NotImplemented("Not implemented")

    def get_input_var_names(self):
      return []

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