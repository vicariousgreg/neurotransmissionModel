# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synaptic cleft bind, modifying the membrane potential of the cell.

from math import exp
from molecule import Receptors
from membrane import ReceptorMembrane

class Dendrite(ReceptorMembrane):
    def __init__(self, receptor=Receptors.AMPA, density=1.0,
                    environment=None, verbose=False):
        """
        Dendrites get neurotransmitters from a synaptic cleft and release them
            back over time.

        |receptor| is the type of receptor on the dendrite membrane.
        |density| is the initial receptor density of the membrane.
        """
        if density > 1.0: raise ValueError
        ReceptorMembrane.__init__(self, receptor, density, environment)
        self.verbose = verbose

    def release(self, destination):
        """
        Stochastically releases neurotransmitters from the receptor proteins.
        Neurotransmitters are released into the given |destination|.
        """
        for mol_id,affinity in self.receptor.affinities.iteritems():
            available = self.get_concentration(mol_id)
            if available == 0.0: continue

            # Stochastically sample bound molecules
            #released = self.environment.beta(available, rate=1.0-affinity)
            released = self.environment.beta(available, rate=5.0)
            #released = available

            if self.verbose: print("Removed %f molecules" % released)

            self.remove_concentration(released, mol_id)
            destination.add_concentration(released, mol_id=mol_id)
