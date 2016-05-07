from molecule import Molecules
from pool import Pool

class PoolCluster:
    def __init__(self, concentrations, environment=None):
        self.pools = dict([
            (mol_id, Pool(concentration, environment))
            for mol_id,concentration in concentrations.iteritems()])

        # Uncomment to use a list of pools instead of a dictionary.
        '''
        self.pools = [Pool(environment=environment) for _ in xrange(Molecules.size)]
        for mol_id,concentration in concentrations.iteritems():
            self.pools[mol_id].set_concentration(concentration)
        '''

    def get_total_concentration(self):
        return sum(self.get_concentration(mol_id) for mol_id in self.analogs)

    def get_concentration(self, mol_id=Molecules.GLUTAMATE):
        return self.pools[mol_id].get_concentration()

    def set_concentration(self, new_concentration, mol_id=Molecules.GLUTAMATE):
        return self.pools[mol_id].set_concentration(new_concentration)

    def add_concentration(self, molecules, mol_id=Molecules.GLUTAMATE):
        return self.pools[mol_id].add_concentration(molecules)

    def remove_concentration(self, molecules, mol_id=Molecules.GLUTAMATE):
        return self.pools[mol_id].remove_concentration(molecules)

