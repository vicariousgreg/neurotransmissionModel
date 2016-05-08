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

from molecule import Molecules, Enzymes, metabolize
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
            dict([(mol.mol_id, 0.0) for mol in Molecules]),
            environment)
        self.enzymes = [enzyme_concentration] * Enzymes.size
        self.verbose = verbose

    def bind(self, membranes):
        # Calculate total receptor count.
        total_receptors = sum(
            membrane.get_available_receptors() for membrane in membranes)
        if total_receptors == 0.0: return

        # Distribute molecules to available membrane receptors.
        for membrane in membranes:
            total_bound = membrane.stochastic_bind(self, total_receptors)
            for mol_id,bound in total_bound.iteritems():
                self.remove_concentration(bound, mol_id)

    def metabolize(self):
        # Metabolize from remaining pool.
        for mol,mol_count in ((mol, self.get_concentration(mol.mol_id)) for mol in Molecules):
            if mol_count <= 0.0: continue
            mol_id = mol.mol_id
            enz_id = mol.enzyme_id
            rate = mol.metab_rate
            enzyme_count = self.enzymes[enz_id]

            destroyed = metabolize(enzyme_count, mol_count, rate, self.environment)
            self.remove_concentration(destroyed, mol_id)
            if self.verbose:
                print("Destroyed %f" % destroyed)
                print("Concentration: %f" % self.get_concentration(mol_id))
