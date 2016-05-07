# Synaptic Cleft Model
#
# Models the space between neurons, including concentration of various
#     neurotransmitters, their corresponding enzymes, and the metabolic
#     processes that affect neurotransmitter concentration.
#
# Presynpatic neurons pump neurotransmitters into the synaptic cleft.
#
# Synaptic neurotransmitters bind stochastically to postsynaptic neuron
#     receptors.

from molecule import Molecules, Analogs, Enzymes, metabolize
from pool_cluster import PoolCluster

class SynapticCleft(PoolCluster):
    def __init__(self, enzyme_concentration=1.0, environment=None, verbose=False):
        """
        A synaptic cleft contains a list of molecule concentrations by id and
            a list of enzyme concentrations by id.
        |enzyme_concentration| is the intial enzyme concentration.
        """
        if enzyme_concentration > 1.0: raise ValueError
        PoolCluster.__init__(self,
            dict([(mol_id, 0.0) for mol_id in xrange(Molecules.size)]),
            environment)
        self.enzymes = [enzyme_concentration] * Enzymes.size
        self.verbose = verbose

    def bind(self, receptor):
        # Distribute molecules to available membrane receptors.
        total_bound = receptor.stochastic_bind(self)
        for mol_id,bound in total_bound.iteritems():
            self.remove_concentration(bound, mol_id)

        self.metabolize()

    def metabolize(self):
        # Metabolize from remaining pool.
        for mol_id,mol_count in enumerate(self.get_concentration(mol) for mol in xrange(Molecules.size)):
            if mol_count <= 0.0: continue
            enz_id,rate,affinity = Analogs[mol_id]
            enzyme_count = self.enzymes[enz_id]

            destroyed = metabolize(enzyme_count, mol_count, rate)
            self.remove_concentration(destroyed, mol_id)
            if self.verbose:
                print("Destroyed %f" % destroyed)
                print("Concentration: %f" % self.get_concentration(mol_id))
