from pathlib import Path

import pytest

from bmi_compose import composed_setup


class SetupModel:
  def __init__(self, name: str, text: str):
    self._name = name
    self._text = text

  def setup(self, *args, **kwargs):
    conf = Path(f"{self._name}.txt")
    conf.write_text(self._text)
    return str(conf.name), str(conf.parent)


def test_composed_setup_returns_single_merged_path(tmp_path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  model1 = SetupModel("m1", "a=1")
  model2 = SetupModel("m2", "b=2")

  merged_path = composed_setup(model1, model2)

  assert isinstance(merged_path, str)
  assert Path(merged_path).exists()
  content = Path(merged_path).read_text()
  assert "a=1" in content
  assert "b=2" in content


def test_composed_setup_requires_setup_method():
  class NoSetup:
    pass

  with pytest.raises(AttributeError):
    composed_setup(NoSetup(), NoSetup())
