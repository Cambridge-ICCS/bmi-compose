# bmi-compose

The [Basic Model Interface](https://github.com/csdms/bmi) is an interface specification
to enable coupling of models to other models and data. The BMI definition has
cross-language support.

This repository provides a set of combinators for __composing__ models implementing the Basic Model Interface.
It implements an algebraic, compositional theory for BMI models to create coupled models easily.

# Status
This code is in an early stage of development.

# Installation

Currently, we recommend Python 3.11 as some the examples
require it for some package dependencies.

1. (Optional, but recommended) Setup a virtual environment:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

2. Install via:

```bash
pip install -e .
```

# Examples

## CEM + Waves Example (`examples/cem_waves_test.ipynb`)

This example demonstrates coupling the Coastline Evolution Model (CEM) with the Waves component using `bmi-compose`.

The examples require the [pymt](https://github.com/csdms/pymt) library and specific model plugins.

1. **Create a conda environment with Python 3.11** (required for `pymt_cem` compatibility):

```bash
conda create -n pymt-cem python=3.11 pymt pymt_cem -c conda-forge -y
```

2. **Install bmi-compose into the conda environment**:

```bash
conda activate pymt-cem
pip install -e .
```

> **Note**: If you have a Python virtual environment (venv) active, deactivate it first with `deactivate` before running the above commands, or use the conda environment's pip directly: 
> ```bash
> /path/to/miniconda3/envs/pymt-cem/bin/python -m pip install -e .
> ```

3. **Open the notebook** (e.g., VS Code or Jupyter) and select the `pymt-cem` kernel.

### Notebook Tips

If `pymt-cem` does not appear in the notebook kernel picker, register it first:

```bash
conda run -n pymt-cem python -m ipykernel install --user --name pymt-cem --display-name "Python (pymt-cem)"
```

## Notes

- The `pymt_cem` package is only available for Python 3.8-3.11, not Python 3.12+.
- The `Waves` model is included with `pymt_cem`.
- You may see deprecation warnings about `pkg_resources` - these can be safely ignored.
- If the pymt modules are downloaded through conda there may be an issue where they are missing the relevant metadata files. In that case go to https://github.com/pymt-lab and clone the desired model. This should solve the issue.

# Running Tests

Install test dependencies:

```bash
python -m pip install -e ".[dev]"
```

For tests that use PyMT model plugins (especially the CEM+Waves comparison),
use a conda environment with Python 3.11:

```bash
conda create -n pymt-cem python=3.11 pymt pymt_cem -c conda-forge -y
conda activate pymt-cem
python -m pip install "setuptools<81" pytest -e .
```

Why `setuptools<81`?

- Current PyMT imports `pkg_resources`, which is removed from newer setuptools builds.
- Pinning setuptools below 81 restores `pkg_resources` and allows `pymt` to import.

Run the full test suite, first set the `PYTHONPATH`

```bash
export set PYTHONPATH="$PWD/src"
```

Then run the tests as:
```bash
python -m pytest -q
```
or to run a single test module:

```bash
python -m pytest -q tests/test_compose_helpers.py
```

Run the CEM+Waves notebook comparison test:

```bash
conda run -n pymt-cem python -m pytest -q -rs tests/test_cem_waves_notebook_comparison.py
```

Notes:

- Some tests depend on optional PyMT model plugins and may be skipped if those models are not available in the active environment.
- For the CEM+Waves comparison test, run from the `pymt-cem` conda environment shown above.
- If you see Python 3.8/3.12 being used unexpectedly, verify the interpreter first with `conda run -n pymt-cem python --version`.