# bmi-compose

The [Basic Model Interface](https://github.com/csdms/bmi) is an interface specification
to enable coupling of models to models and models to data. The BMI definition has
cross language support.

This repository provides a set of combinators for __composing__ models implementing the Basic Model Interface.
It implements an algebraic, compositional theory for BMI models that enables coupled modles by composition.

# Status
This code is in very early stages of development.

# Installation

Currently, we recommend Python 3.11 as some the examples
require it for some package depenencies.

1. (Optional, but recommended) Setup a virtual environment:

```bash
python3.11 -m venv venv
source venv/activate/bin
```

2. Install via:

```bash
pip install -e .
```

# Examples

## CEM + Waves Example (`examples/cem_waves_test.ipynb`)

This example demonstrates coupling the Coastline Evolution Model (CEM) with the Waves component using `bmi-compose`.

The examples require the [pymt](https://github.com/csdms/pymt) library and specific model plugins.

1. **Create an activate conda environment with Python 3.11** (required for `pymt_cem` compatibility):

```bash
conda create -n pymt-cem python=3.11 pymt pymt_cem -c conda-forge -y
conda activate pymt-cem
```

2. **Open the notebook** (e.g., VS Code or Jupyter) and select the `pymt-cem` kernel.

## Notes

- The `pymt_cem` package is only available for Python 3.8-3.11, not Python 3.12+.
- The `Waves` model is included with `pymt_cem`.
- You may see deprecation warnings about `pkg_resources` - these can be safely ignored.
- If the pymt modules are downloaded through conda there may be an issue where they are missing the  relevant metadata files. In that case go to https://github.com/pymt-lab and clone the desired model. This should solve the issue.
