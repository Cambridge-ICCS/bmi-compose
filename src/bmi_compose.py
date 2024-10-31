from bmipy import Bmi
from numpy import ndarray

def compose(bmi1 : Bmi, bmi2 : Bmi, interface : list[str]) -> Bmi:
    """Compose two BMI models into a single one with an ordering where
     the first model argument is initialized, updated, and finalised first.

    Parameters
    ----------
    bmi1 : Bmi
    The first BMI model (who goes first).

    bmi2 : Bmi
    The second BMI model.

    interface : list[str]
    The list of variables to be shared between the two models.

    Returns
    -------
    composed_bmi : Bmi
    The composed BMI model.
    """
    # check that the models are compatible
    # check that types and sizes cohere
    for i in bmi1.get_input_var_names() + bmi1.get_output_var_names():
        if i in bmi2.get_input_var_names() | i in bmi2.get_output_var_names():
            if bmi1.get_var_type(i) != bmi2.get_var_type(i):
                raise ValueError("Models are not compatible in types at " + i)
            if bmi1.get_var_nbytes(i) != bmi2.get_var_nbytes(i):
                raise ValueError("Models are not compatible in sizes at " + i)

    # check and calculating cycling
    bmi1_cycles : int = 1
    bmi2_cycles : int = 1
    max_time_step : float = 0

    if bmi1.get_time_step() % bmi2.get_time_step() == 0:
        bmi2_cycles = int(bmi1.get_time_step() / bmi2.get_time_step())
        time_step = bmi1.get_time_step()

    elif bmi2.get_time_step() % bmi1.get_time_step() == 0:
        bmi1_cycles = int(bmi2.get_time_step() / bmi1.get_time_step())
        time_step = bmi2.get_time_step()

    else:
        raise ValueError("Time steps are incompatible (one is not a factor of the other): dt1 = " + bmi1.get_time_step() + " and dt2 = " + bmi2.get_time_step())

    # Otherwise, build the composed class
    class ComposedBmi(Bmi):
        def initialize(self, config_file):
            bmi1.initialize(config_file)
            bmi2.initialize(config_file)
            return self

        def update(self):
            # At most one model with have multiple cycles run
            assert(bmi1_cycles == 1 | bmi2_cycles == 1)

            def bmi1_run():
              # Run bmi1 cycles
              for i in range(1, bmi1_cycles):
                  bmi1.update()

              # link bmi1 values to bmi2
              for i in interface:
                bmi2.set_value(i, bmi1.get_value(i))

            def bmi2_run():
              # Run bmi2 cycles
              for i in range(1, bmi2_cycles):
                  bmi2.update()

              # link back bmi2 values to bmi1
              for i in interface:
                  bmi1.set_value(i, bmi2.set_value(i))

              # left-biased run
              bmi1_run()
              bmi2_run()

            return self

        def update_until(self, time):
            bmi1.update_until(time)

            # link bm1 values to bmi2
            for i in interface:
                bmi2.set_value(i, bmi1.get_value(i))

            bmi2.update_until(time)

            # link back bmi2 values to bmi1
            for i in interface:
                bmi1.set_value(i, bmi2.set_value(i))
            return self

        def finalize(self):
            bmi1.finalize()
            bmi2.finalize()
            return self

        def get_component_name(self):
            return (bmi1.get_component_name() + " >< " + bmi2.get_component_name())

        def get_input_var_names(self):
            return union(bmi1.get_input_var_names(), bmi2.get_input_var_names())

        def get_output_var_names(self):
            return union(bmi1.get_output_var_names(), bmi2.get_output_var_names())

        def get_var_type(self, name):
            if name in bmi1.get_input_var_names():
                return bmi1.get_var_type(name)
            else:
                return bmi2.get_var_type(name)

        def get_var_units(self, name):
            if name in bmi1.get_input_var_names() + bmi1.get_output_var_names():
                return bmi1.get_var_units(name)
            else:
                return bmi2.get_var_units(name)

        def get_var_nbytes(self, name):
            if name in bmi1.get_input_var_names() + bmi1.get_output_var_names():
                return bmi1.get_var_nbytes(name)
            else:
                return bmi2.get_var_nbytes(name)

        def get_var_location(self, name: str) -> str:
            if name in bmi1.get_input_var_names() + bmi1.get_output_var_names():
                return bmi1.get_var_location(name)
            else:
                return bmi2.get_var_location(name)

        def set_value(self, name: str, values: ndarray) -> None:
            bmi1.set_value(name, values)
            bmi2.set_value(name, values)

        def set_value_at_indices(self, name: str, inds: ndarray, src: ndarray) -> None:
            bmi1.set_value_at_indices(name, inds, src)
            bmi2.set_value_at_indices(name, inds, src)

        def get_time_step(self) -> float:
            return max_time_step

        def get_current_time(self) -> float:
            assert(bmi1.get_current_time() == bmi2.get_current_time())
            return bmi1.get_current_time()

    return ComposedBmi()

# Helpers

def union(xs, ys):
    return (xs + [y for y in ys if y not in xs])