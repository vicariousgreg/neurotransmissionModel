# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synaptic cleft bind, modifying the membrane potential of the cell.

from multiprocessing import Value
from molecule import Receptors

class Dendrite:
    def __init__(self, receptor=Receptors.AMPA, density=1.0,
                    strength=25, environment=None, verbose=False):
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
        self.environment = environment
        self.env_id = environment.register(self.stable_voltage)
        self.verbose = verbose

    def get_bound(self):
        """
        NEEDS TO BE THREAD SAFE
        """
        return self.environment.get(self.env_id)

    def set_bound(self, concentration):
        """
        NEEDS TO BE THREAD SAFE
        """
        self.environment.set(self.env_id, concentration)

    def bind(self, concentration):
        """
        NEEDS TO BE THREAD SAFE
        """
        self.environment.adjust(self.env_id, concentration)

    def activate(self, neuron):
        self.protein.activation_function(self.strength,
            self.get_bound(),
            neuron)
