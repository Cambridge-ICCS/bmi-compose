from bmipy import Bmi


class IdentityBmi(Bmi):
  """An identity BMI model that does nothing but can be composed with another model.
  
  This class implements the BMI interface as an identity element for composition,
  such that `compose(x, IdentityBmi()) ≈ x` and `compose(IdentityBmi(), x) ≈ x`.
  
  The identity model has no input or output variables, performs no computation
  during update, and returns neutral values for all BMI methods.
  
  Limitations:
    - Start times must match (identity uses 0.0)
    - Time units must match (identity uses "s")
    - Composed model name will diwffer: "ModelName -> Identity" vs "ModelName"
    - Time step compatibility constraints still apply
  """

  def __init__(self):
    # Self-reference for compose compatibility (compose accesses .bmi attribute)
    self.bmi = self

  def setup(self, *args, **kwargs):
    return args, kwargs

  def initialize(self, *args, **kwargs):
    return self

  def update(self):
    return self

  def update_until(self, time):
    return self

  def finalize(self):
    return self

  def get_component_name(self):
    return "Identity"

  def get_input_var_names(self):
    return []

  def get_output_var_names(self):
    return []

  def get_value(self, name, out=None, units=None, angle=None, at=None, method=None):
    return None

  def set_value(self, name, value):
    return None

  def get_value_ptr(self, name):
    return None

  def get_value_at_indices(self, name, indices):
    return None

  def set_value_at_indices(self, name, indices, value):
    return None

  def get_current_time(self):
    return 0.0

  def get_start_time(self):
    return 0.0

  def get_end_time(self):
    return float('inf')

  def get_time_step(self):
    return 1.0

  def get_time_units(self):
    return "s"

  def get_var_grid(self, name):
    return 0

  def get_var_type(self, name):
    return "float64"

  def get_var_units(self, name):
    return ""

  def get_var_itemsize(self, name):
    return 8

  def get_var_nbytes(self, name):
    return 8

  def get_var_location(self, name):
    return "node"

  def get_grid_rank(self, grid):
    return 0

  def get_grid_size(self, grid):
    return 0

  def get_grid_type(self, grid):
    return "scalar"

  def get_grid_shape(self, grid, shape):
    return shape

  def get_grid_spacing(self, grid, spacing):
    return spacing

  def get_grid_origin(self, grid, origin):
    return origin

  def get_grid_x(self, grid, x):
    return x

  def get_grid_y(self, grid, y):
    return y

  def get_grid_z(self, grid, z):
    return z

  def get_grid_node_count(self, grid):
    return 0

  def get_grid_edge_count(self, grid):
    return 0

  def get_grid_face_count(self, grid):
    return 0

  def get_grid_edge_nodes(self, grid, edge_nodes):
    return edge_nodes

  def get_grid_face_edges(self, grid, face_edges):
    return face_edges

  def get_grid_face_nodes(self, grid, face_nodes):
    return face_nodes

  def get_grid_nodes_per_face(self, grid, nodes_per_face):
    return nodes_per_face

  def get_input_item_count(self):
    return 0

  def get_output_item_count(self):
    return 0