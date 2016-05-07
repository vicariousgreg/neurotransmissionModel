from stochastic import beta
from pool import Pool
from molecule import Molecules, Analogs
from pool_cluster import PoolCluster

class Membrane(PoolCluster):
    def __init__(self, native_mol_id, baseline_concentration=0.0, environment=None):
        self.native_mol_id = native_mol_id
        self.analogs = [molecule for molecule in xrange(Molecules.size)
                            if Analogs[molecule][0] == native_mol_id]
        concentrations = dict([
            (mol_id, 0.0)
            for mol_id in self.analogs])
        concentrations[native_mol_id] = baseline_concentration
        PoolCluster.__init__(self, concentrations, environment)

    def get_available_spots(self):
        raise ValueError("Cannot simulate abstract class!")

    def get_native_concentration(self):
        return self.get_concentration(self.native_mol_id)

    def stochastic_bind(self, source):
        total_bound = dict()
        for analog in self.analogs:
            available_mols = source.get_concentration(analog)
            affinity = Analogs[analog][2]

            # Check available molecules
            if available_mols <= 0: continue

            # Sample available molecules
            sample = beta(available_mols, rate=2)
            bound = sample * self.get_available_spots() * affinity

            if self.verbose: print("Bound %f" % bound)

            # Bind sampled molecules
            self.pools[analog].add_concentration(bound)
            total_bound[analog] = bound
        return total_bound
