# Pool Cluster
#
# Models a collection of individual molecule pools.

from molecule import Molecule_IDs

class PoolCluster:
    def __init__(self, concentrations, environment=None):
        """
        Creates a cluster of pools according to a |concentration| dictionary
            of molecule identifiers to initial concentrations.
        The |environment| contains the actual concentrations so that they can
            be managed during timesteps externally.
        """
        self.pool_ids = dict([
            (mol_id, environment.create_pool(concentration))
            for mol_id,concentration in concentrations.iteritems()])
        self.environment = environment

        # Uncomment to use a list of pools instead of a dictionary.
        '''
        self.pool_ids = [Pool(environment=environment) for _ in xrange(Molecule_IDs.size)]
        for mol_id,concentration in concentrations.iteritems():
            self.pool_ids[mol_id].set_concentration(concentration)
        '''

    def get_total_concentration(self):
        return sum(self.get_concentration(mol_id) for mol_id in self.pool_ids)

    def get_concentration(self, mol_id=Molecule_IDs.GLUTAMATE):
        return self.environment.get_concentration(self.pool_ids[mol_id])

    def set_concentration(self, new_concentration, mol_id=Molecule_IDs.GLUTAMATE):
        return self.environment.set_concentration(self.pool_ids[mol_id], new_concentration)

    def add_concentration(self, molecules, mol_id=Molecule_IDs.GLUTAMATE):
        return self.environment.add_concentration(self.pool_ids[mol_id], molecules)

    def remove_concentration(self, molecules, mol_id=Molecule_IDs.GLUTAMATE):
        return self.environment.remove_concentration(self.pool_ids[mol_id], molecules)

