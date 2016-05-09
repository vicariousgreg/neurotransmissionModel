# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synaptic cleft bind, modifying the membrane potential of the cell.

from molecule import Receptors
from pool_cluster import PoolCluster

class Dendrite(PoolCluster):
    def __init__(self, receptor=Receptors.AMPA, density=1.0, environment=None, verbose=False):
        """
        Dendrites hold receptors that are activated by neurochemicals in the
            synaptic cleft.

        |receptor| is the type of receptor on the dendrite membrane.
        |density| is the initial receptor density of the membrane.
        """
        concentrations = dict([(mol_id, 0.0) for mol_id in receptor.affinities])
        PoolCluster.__init__(self, concentrations, environment)

        if density > 1.0: raise ValueError
        self.protein = receptor
        self.density = density
        self.native_mol_id = receptor.native_mol_id
        self.affinities = receptor.affinities
        self.verbose = verbose

    def get_available_proteins(self, mol_id):
        return self.density
