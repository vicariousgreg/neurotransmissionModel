# Pool
#
# Pool is an abstract class that contains concentrations of molecules.

from component import Component
from molecule import Molecules

class Pool(Component):
    def __init__(self, baseline_concentration=0.0):
        super(Component, self).__init__()
        self.set_concentration(baseline_concentration)

    def get_concentration(self):
        return self.concentration

    def set_concentration(self, new_concentration):
        if new_concentration < 0.0: raise ValueError
        self.concentration = new_concentration
        return new_concentration

    def add_concentration(self, molecules):
        self.concentration += molecules
        return self.concentration

    def remove_concentration(self, molecules):
        if molecules > self.concentration: raise ValueError
        self.concentration -= molecules
        return self.concentration

    @staticmethod
    def transfer(from_pool, to_pool, molecules):
        pass
