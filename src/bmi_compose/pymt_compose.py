from pathlib import Path

from .compose import composeConfig


def composed_setup(model1, model2, *args, suffix: str = ".txt", **kwargs) -> str:
  """Build a merged config path for two PyMT-style models.

  This helper is intended for wrappers that expose a ``setup`` method returning
  ``(config_filename, config_directory)``. The returned value is a single config
  path string suitable for ``compose(...).initialize(config_file)``.
  """

  if not hasattr(model1, "setup") or not hasattr(model2, "setup"):
    raise AttributeError("Both models must define a setup method")

  defaults1 = model1.setup(*args, **kwargs)
  defaults2 = model2.setup(*args, **kwargs)

  path1 = Path(defaults1[1], defaults1[0])
  path2 = Path(defaults2[1], defaults2[0])

  merged_name, merged_parent = composeConfig(path1, path2, suffix=suffix)
  return str(Path(merged_parent, merged_name))
