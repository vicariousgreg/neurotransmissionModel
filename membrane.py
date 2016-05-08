#from molecule import Molecules, Analogs
from pool_cluster import PoolCluster

class Membrane(PoolCluster):
    def __init__(self, protein, density, environment=None):
        self.native_mol_id = protein.native_mol_id
        concentrations = dict([
            (mol_id, 0.0)
            for mol_id in protein.affinities])
        self.density = density
        self.affinities = protein.affinities
        PoolCluster.__init__(self, concentrations, environment)

    def get_available_receptors(self):
        raise ValueError("Cannot simulate abstract class!")

    def get_native_concentration(self):
        return self.get_concentration(self.native_mol_id)

    def stochastic_bind(self, source, total_receptors):
        total_bound = dict()
        for mol_id, affinity in self.affinities.iteritems():
            fraction = self.get_available_receptors() / total_receptors
            available_mols = source.get_concentration(mol_id) * fraction

            # Check available molecules
            if available_mols <= 0: continue

            # Sample available molecules
            sample = self.environment.beta(available_mols, rate=2)
            bound = sample * self.get_available_receptors() * affinity

            if self.verbose: print("Bound %f" % bound)

            # Bind sampled molecules
            self.add_concentration(bound, mol_id)
            total_bound[mol_id] = bound
        return total_bound

class ReceptorMembrane(Membrane):
    def __init__(self, receptor, density=1.0, environment=None):
        Membrane.__init__(self, receptor, density, environment)
        self.receptor = receptor

    def get_available_receptors(self):
        return self.density - self.get_total_concentration()

class TransporterMembrane(Membrane):
    def __init__(self, transporter, density=1.0, capacity=1.0, environment=None):
        Membrane.__init__(self, transporter, density, environment)
        self.transporter = transporter
        self.capacity = capacity
        self.set_concentration(capacity, transporter.native_mol_id)

    def get_available_receptors(self):
        return min(self.capacity-self.get_native_concentration(), self.density)
