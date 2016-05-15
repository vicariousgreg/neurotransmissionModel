# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synaptic cleft bind, modifying the membrane potential of the cell.

from molecule import Receptors
from membrane import ReceptorMembrane

class Dendrite(ReceptorMembrane):
    def __init__(self, receptor=Receptors.AMPA, density=1.0, strength=0.05,
                        single_molecule=None, environment=None, verbose=False):
        """
        Dendrites hold receptors that are activated by neurochemicals in the
            synaptic cleft.

        |receptor| is the type of receptor on the dendrite membrane.
        |density| is the initial receptor density of the membrane.
        """
        if density > 1.0: raise ValueError
        ReceptorMembrane.__init__(self, receptor, density, environment)
        self.strength = strength
        self.verbose = verbose

        if single_molecule:
            self.get_activation = lambda: self.strength * self.get_native_concentration
        else:
            self.get_activation = self.get_all_activation

    def get_all_activation(self):
        return self.strength * self.get_total_concentration()
