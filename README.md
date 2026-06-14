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

## Notes

- The `pymt_cem` package is only available for Python 3.8-3.11, not Python 3.12+.
- The `Waves` model is included with `pymt_cem`.
- You may see deprecation warnings about `pkg_resources` - these can be safely ignored.
- If the pymt modules are downloaded through conda there may be an issue where they are missing the relevant metadata files. In that case go to https://github.com/pymt-lab and clone the desired model. This should solve the issue.
