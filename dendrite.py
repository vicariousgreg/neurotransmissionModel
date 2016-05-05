# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synapse bind, modifying the membrane potential of the cell.

from math import exp
from stochastic import beta
from pool import Pool
from membrane import stochastic_release

from molecule import Molecules

class Dendrite(Pool):
    def __init__(self, initial_size=1.0, mol_id=Molecules.GLUTAMATE,
                    release_rate=1, verbose=False):
        """
        Dendrites get neurotransmitters from a synapse and release them back
            over time.

        |mol_id| is the identifier for the neurotransmitter to be bound.
        |initial_size| is the initial size of the receptor pool.
        |release_rate| controls the release of neurotransmitter back
            into the synapse.  Higher values increase the rate of release.
        """
        if initial_size > 1.0: raise ValueError
        super(Dendrite, self).__init__(baseline_concentration=0.0)

        self.size = initial_size
        self.mol_id = mol_id
        self.release_rate = release_rate 
        self.verbose = verbose
        self.destination = None

    def get_available_spots(self):
        return self.size - self.get_concentration()

    def step(self, time):
        """
        Runs a time step.
        Releases molecules.
        """
        released = stochastic_release(self.get_concentration(), self.release_rate)
        self.remove_concentration(released)
        if self.destination:
            self.destination.add_concentration(released, mol_id=self.mol_id)
