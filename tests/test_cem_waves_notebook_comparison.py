from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest


ANGLE_NAME = "sea_surface_water_wave__azimuth_angle_of_opposite_of_phase_velocity"
BEDLOAD_NAME = "land_surface_water_sediment~bedload__mass_flow_rate"
WAVE_HEIGHT_NAME = "sea_surface_water_wave__height"
WAVE_PERIOD_NAME = "sea_surface_water_wave__period"
DEPTH_NAME = "sea_water__depth"


def _import_pymt_or_skip():
  try:
    import pymt
  except Exception as exc:  # pragma: no cover - environment-dependent
    pytest.skip(f"PyMT import unavailable in this environment: {exc}")
  return pymt


def _get_pymt_model_registry_or_skip(pymt_module):
  if hasattr(pymt_module, "MODELS"):
    return pymt_module.MODELS

  if hasattr(pymt_module, "models"):
    return pymt_module.models

  try:
    import pymt.models as models
    return models
  except Exception as exc:  # pragma: no cover - environment-dependent
    pytest.skip(f"PyMT model registry unavailable in this environment: {exc}")


def _import_compose_or_skip():
  try:
    from bmi_compose import composeConfig, compose_sequentially
    return compose_sequentially, composeConfig
  except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))
    try:
      from bmi_compose import composeConfig, compose_sequentially
      return compose_sequentially, composeConfig
    except Exception as exc:  # pragma: no cover - environment-dependent
      pytest.skip(f"bmi_compose import unavailable in this environment: {exc}")
  except Exception as exc:  # pragma: no cover - environment-dependent
    pytest.skip(f"bmi_compose import unavailable in this environment: {exc}")


def _setup_waves_with_seed_if_supported(waves):
  for seed_key in ("seed", "random_seed", "rng_seed"):
    try:
      return waves.setup(**{seed_key: 42})
    except TypeError:
      continue
  return waves.setup()


def _run_manual_notebook_style(n_steps: int):
  pymt = _import_pymt_or_skip()
  models = _get_pymt_model_registry_or_skip(pymt)
  cem, waves = models.Cem(), models.Waves()

  cem_args = cem.setup(number_of_rows=80, number_of_cols=120, grid_spacing=200.0)
  cem.initialize(*cem_args)
  waves_args = _setup_waves_with_seed_if_supported(waves)
  waves.initialize(*waves_args)

  grid_id = cem.get_var_grid(DEPTH_NAME)
  shape = cem.get_grid_shape(grid_id)

  qs = np.zeros(shape, dtype=float)
  qs[0, shape[1] // 2] = 750.0

  waves.set_value(
      "sea_shoreline_wave~incoming~deepwater__ashton_et_al_approach_angle_asymmetry_parameter",
      0.3,
  )
  waves.set_value(
      "sea_shoreline_wave~incoming~deepwater__ashton_et_al_approach_angle_highness_parameter",
      0.7,
  )
  cem.set_value(WAVE_HEIGHT_NAME, 2.0)
  cem.set_value(WAVE_PERIOD_NAME, 7.0)

  for _ in range(n_steps):
    waves.update()
    angle = waves.get_value(ANGLE_NAME)
    cem.set_value(ANGLE_NAME, angle)
    cem.set_value(BEDLOAD_NAME, qs)
    cem.update()

  z = np.empty(shape, dtype=float)
  cem.get_value(DEPTH_NAME, out=z)

  waves.finalize()
  cem.finalize()
  return z


def _run_composed_notebook_style(n_steps: int):
  compose_sequentially, composeConfig = _import_compose_or_skip()
  pymt = _import_pymt_or_skip()
  models = _get_pymt_model_registry_or_skip(pymt)
  cem, waves = models.Cem(), models.Waves()
  cem_compose = compose_sequentially(waves.bmi, cem.bmi)

  cem_args = cem.setup(number_of_rows=80, number_of_cols=120, grid_spacing=200.0)
  waves_args = _setup_waves_with_seed_if_supported(waves)
  waves_path = Path(waves_args[1], waves_args[0])
  cem_path = Path(cem_args[1], cem_args[0])
  merged_name, merged_parent = composeConfig(waves_path, cem_path)
  merged_config = str(Path(merged_parent, merged_name))
  cem_compose.initialize(merged_config)

  grid_id = cem.get_var_grid(DEPTH_NAME)
  shape = cem.get_grid_shape(grid_id)

  qs = np.zeros(shape, dtype=float)
  qs[0, shape[1] // 2] = 750.0

  cem_compose.set_value(
      "sea_shoreline_wave~incoming~deepwater__ashton_et_al_approach_angle_asymmetry_parameter",
      np.array(0.3),
  )
  cem_compose.set_value(
      "sea_shoreline_wave~incoming~deepwater__ashton_et_al_approach_angle_highness_parameter",
      np.array(0.7),
  )
  cem_compose.set_value(WAVE_HEIGHT_NAME, np.array(2.0))
  cem_compose.set_value(WAVE_PERIOD_NAME, np.array(7.0))

  for _ in range(n_steps):
    cem_compose.set_value(BEDLOAD_NAME, np.array(qs))
    cem_compose.update()

  z = np.empty(shape, dtype=float)
  cem_compose.get_value(DEPTH_NAME, z)

  cem_compose.finalize()
  return z


def test_cem_waves_manual_and_composed_notebooks_agree(tmp_path, monkeypatch):
  """Compare notebook-style manual coupling against composed coupling output."""
  monkeypatch.chdir(tmp_path)

  manual_depth = _run_manual_notebook_style(n_steps=200)
  composed_depth = _run_composed_notebook_style(n_steps=200)

  assert manual_depth.shape == composed_depth.shape
  np.testing.assert_allclose(manual_depth, composed_depth, rtol=1e-6, atol=1e-4)
