# Pool
#
# Pool is an abstract class that contains concentrations of molecules.

from molecule import Molecules

class Pool:
    def __init__(self, baseline_concentration=0.0, environment=None):
        if environment is None: raise ValueError
        self.environment = environment
        self.pool_id = environment.get_id()
        self.set_concentration(baseline_concentration)

    def get_concentration(self):
        return self.environment.get_concentration(self.pool_id)

    def set_concentration(self, new_concentration):
        if new_concentration < 0.0: raise ValueError
        self.environment.set_concentration(self.pool_id, new_concentration)

    def add_concentration(self, molecules):
        self.environment.add_concentration(self.pool_id, molecules)

    def remove_concentration(self, molecules):
        self.environment.remove_concentration(self.pool_id, molecules)
