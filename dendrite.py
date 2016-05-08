# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synaptic cleft bind, modifying the membrane potential of the cell.

from math import exp
from molecule import Receptors
from membrane import ReceptorMembrane

class Dendrite(ReceptorMembrane):
    def __init__(self, receptor=Receptors.AMPA, initial_size=1.0,
                    environment=None, verbose=False):
        """
        Dendrites get neurotransmitters from a synaptic cleft and release them
            back over time.

        |mol_id| is the identifier for the neurotransmitter to be bound.
        |initial_size| is the initial size of the receptor pool.
        """
        if initial_size > 1.0: raise ValueError
        ReceptorMembrane.__init__(self, receptor, initial_size, environment)
        self.verbose = verbose

    def release(self, destination):
        for mol_id,affinity in self.receptor.affinities.iteritems():
            available = self.get_concentration(mol_id)
            if available == 0.0: continue

            # Stochastically sample bound molecules
            released = self.environment.beta(available, rate=1.0-affinity)

            if self.verbose: print("Removed %f molecules" % released)

            self.remove_concentration(released, mol_id)
            if destination:
                destination.add_concentration(released, mol_id=mol_id)
