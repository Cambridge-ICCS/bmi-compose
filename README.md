# bmi-compose

The [Basic Model Interface](https://github.com/csdms/bmi) is an interface specification
to enable coupling of models to models and models to data. The BMI definition has
cross language support.

This repository provides a set of combinators for __composing__ models implementing the Basic Model Interface.
It implements an algebraic, compositional theory for BMI models that enables coupled modles by composition.

# Status
This code is in very early stages of development.

# Notes
If the pymt modules are downloaded through anaconda there may be an issue where they are missing the 
relevant metadata files. In that case go to https://github.com/pymt-lab and clone the desired model.
This should solve the issue.

# Examples

The examples require the [pymt](https://github.com/csdms/pymt) library. 

```
conda create -n pymt python=3
config --add channels conda-forge
conda activate pymt
conda install pymt
```