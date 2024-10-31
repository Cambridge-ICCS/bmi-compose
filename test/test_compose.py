from bmipy import Bmi
from bmi_compose import compose

class Simple(Bmi):
  def __init__(self, name : str):
    self.name = name

  def get_component_name(self):
    return self.name

  def initialize(self):
    raise NotImplemented("Not implemented")

  def finalize(self):
    raise NotImplemented("Not implemented")

  def update(self):
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

  def get_value(self):
    raise NotImplemented("Not implemented")

  def set_value(self):
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

def test_name():
  x = Simple("x")
  y = Simple("y")
  z = compose(x, y, [])
  assert z.get_component_name() == "x <> y"
