import pytest

from bmi_compose import IdentityBmi, compose

class CounterBmi:
  """Minimal BMI-like model for identity composition tests."""

  def __init__(self, name="Counter", start=0.0, step=1.0, delta=1.0):
    self.bmi = self
    self._name = name
    self._x = float(start)
    self._time = 0.0
    self._step = float(step)
    self._delta = float(delta)

  def initialize(self, *args, **kwargs):
    return self

  def update(self):
    self._x += self._delta
    self._time += self._step
    return self

  def update_until(self, time):
    while self._time < time:
      self.update()
    return self

  def finalize(self):
    return self

  def get_component_name(self):
    return self._name

  def get_input_var_names(self):
    return ["x"]

  def get_output_var_names(self):
    return ["x"]

  def get_value(self, name, out=None, units=None, angle=None, at=None, method=None):
    if name != "x":
      raise KeyError(name)
    return self._x

  def set_value(self, name, value):
    if name != "x":
      raise KeyError(name)
    self._x = float(value)

  def get_current_time(self):
    return self._time

  def get_start_time(self):
    return 0.0

  def get_end_time(self):
    return 10.0

  def get_time_step(self):
    return self._step

  def get_time_units(self):
    return "s"


@pytest.fixture
def merged_config(tmp_path, monkeypatch):
  """Create a merged config that compose.initialize can split."""
  monkeypatch.chdir(tmp_path)
  merged = tmp_path / "merged_conf.txt"
  merged.write_text("cfg1\n\nStart of config file 2: \n\ncfg2")
  return merged


def test_right_identity_preserves_state_evolution(merged_config):
  baseline = CounterBmi(start=2.0, step=1.0, delta=0.25)
  baseline.initialize()

  model = CounterBmi(start=2.0, step=1.0, delta=0.25)
  composed = compose(model, IdentityBmi())
  composed.initialize(str(merged_config))

  for _ in range(5):
    baseline.update()
    composed.update()

  assert composed.get_value("x") == pytest.approx(baseline.get_value("x"))
  assert composed.get_current_time() == pytest.approx(baseline.get_current_time())


def test_left_identity_preserves_state_evolution(merged_config):
  baseline = CounterBmi(start=1.0, step=1.0, delta=2.0)
  baseline.initialize()

  model = CounterBmi(start=1.0, step=1.0, delta=2.0)
  composed = compose(IdentityBmi(), model)
  composed.initialize(str(merged_config))

  for _ in range(4):
    baseline.update()
    composed.update()

  assert composed.get_value("x") == pytest.approx(baseline.get_value("x"))
  assert model.get_current_time() == pytest.approx(baseline.get_current_time())


def test_identity_composition_keeps_variable_interface_for_x(merged_config):
  model = CounterBmi(start=3.0, step=1.0, delta=1.5)
  composed = compose(model, IdentityBmi())
  composed.initialize(str(merged_config))

  composed.set_value("x", 42.0)

  assert composed.get_value("x") == pytest.approx(42.0)