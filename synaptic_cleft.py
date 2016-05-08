# Synaptic Cleft Model
#
# Models the space between neurons, including concentration of various
#     neurotransmitters, their corresponding enzymes, and the metabolic
#     processes that affect neurotransmitter concentration.
#
# Presynpatic neurons pump neurotransmitters into the synaptic cleft.
#
# Synaptic neurotransmitters bind stochastically to postsynaptic neuron
#     receptors and presynaptic transporters.

from molecule import Molecules, Enzymes, metabolize
from pool_cluster import PoolCluster

class SynapticCleft(PoolCluster):
    def __init__(self, enzyme_concentration=1.0, environment=None, verbose=False):
        """
        A synaptic cleft contains pools of molecules and enzymes.
        |enzyme_concentration| is the intial concentration of enzymes.
        """
        if enzyme_concentration > 1.0: raise ValueError
        PoolCluster.__init__(self,
            dict([(mol.mol_id, 0.0) for mol in Molecules]),
            environment)
        self.enzymes = [enzyme_concentration] * Enzymes.size
        self.verbose = verbose

    def bind(self, membranes):
        """
        Stochastically binds molecules to the given |membranes|.
        Molecule availablity is determined by the relative concentration of
            proteins on a given membrane compared to the total across all
            membranes.
        """
        # Calculate total protein count.
        total_proteins = sum(
            membrane.get_available_proteins() for membrane in membranes)
        if total_proteins == 0.0: return

        # Distribute molecules to available membrane proteins.
        for membrane in membranes:
            total_bound = membrane.stochastic_bind(self, total_proteins)
            for mol_id,bound in total_bound.iteritems():
                self.remove_concentration(bound, mol_id)

    def metabolize(self):
        """
        Stochastically metabolizes molecules in the pools according to the
            concentration of appropriate enzymes.
        """
        for mol in Molecules:
            mol_count = self.get_concentration(mol.mol_id)
            if mol_count <= 0.0: continue

            mol_id = mol.mol_id
            enz_id = mol.enzyme_id
            rate = mol.metab_rate
            enzyme_count = self.enzymes[enz_id]

            destroyed = metabolize(enzyme_count, mol_count, rate, self.environment)
            self.remove_concentration(destroyed, mol_id)
            if self.verbose:
                print("Destroyed %f of %s" % (destroyed, mol.name))
                print("New concentrations: %f" % self.get_concentration(mol_id))
