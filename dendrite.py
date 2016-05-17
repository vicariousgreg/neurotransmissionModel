# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synaptic cleft bind, modifying the membrane potential of the cell.

from molecule import Receptors

class Dendrite:
    def __init__(self, receptor=Receptors.AMPA, density=1.0,
                    strength=0.05, verbose=False):
        """
        Dendrites hold receptors that are activated by neurochemicals in the
            synaptic cleft.

        |receptor| is the type of receptor on the dendrite membrane.
        |density| is the initial receptor density of the membrane.
        """
        if density > 1.0: raise ValueError
        self.protein = receptor
        self.native_mol_id = receptor.native_mol_id
        self.density = density
        self.affinities = receptor.affinities
        self.strength = strength
        self.bound = 0.0
        self.verbose = verbose

    def get_concentration(self, mol_id=None):
        """
        NEEDS TO BE THREAD SAFE
        """
        return self.bound

    def set_bound(self, concentration):
        """
        NEEDS TO BE THREAD SAFE
        """
        self.bound = concentration

    def bind(self, concentration):
        """
        NEEDS TO BE THREAD SAFE
        """
        self.bound += concentration

    def get_activation(self):
        return self.strength * self.bound
