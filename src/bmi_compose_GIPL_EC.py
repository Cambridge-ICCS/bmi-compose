import pymt.models
import numpy as np
from bmipy import Bmi


ec = pymt.models.ECSimpleSnow()
gipl = pymt.models.GIPL()

def ectest(bmi1 : Bmi, bmi2 : Bmi, interface : list[str]) -> Bmi:


    
    class ComposedBmi(Bmi):

        def setup(self):
            ec_defaults = bmi1.setup(".")
            gipl_defaults = bmi2.setup(".")


        def initialize(self, config_file):
            bmi1.initialize(config_file)
            bmi2.initialize(config_file)
            return self

        def update(self, specifics : list[str] , units : dict{str}, set_conversions : dict()):
            # At most one model with have multiple cycles run

            def bmi1_run():
              # Run bmi1 cycles
                bmi1.update()


        return self