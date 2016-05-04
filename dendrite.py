# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synapse bind, modifying the membrane potential of the cell.

from math import exp
from stochastic import beta

from molecule import Molecules

class Dendrite:
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
        self.mol_id = mol_id
        self.size = initial_size
        self.release_rate = release_rate 
        self.concentration = 0.0
        self.verbose = verbose
        self.synapse = None

    def set_synapse(self, synapse):
        """
        Connects the dendrite to a synapse.
        """
        self.synapse = synapse

    def step(self, time):
        """
        Runs a time step.
        First, molecules are released.
        Then, molecules are retrieved from the synapse based on a sampled count
            and the size of the receptor pool.
        """
        # Check available molecules
        available = self.synapse.get(self.mol_id)

        # Release bound molecules
        # This is done after bind sampling to ensure the receptors do not
        #     simply rebind molecules immediately after they are released.
        self.release()

        if available <= 0: return

        missing = self.size - self.concentration

        # Sample available molecules
        sample = beta(available, rate=10)
        bound = sample * missing

        if self.verbose:
            print("Dendrite: %f" % self.concentration)
            print("Bound %f molecules" % bound)

        # Bind sampled molecules
        self.synapse.remove(self.mol_id, bound)
        self.concentration += bound

    def release(self):
        """
        Releases some neurotransmitters back into the synapse.
        """
        # Stochastically sample bound molecules
        sample = beta(self.concentration, rate=self.release_rate)

        # Release sampled molecules
        self.concentration -= sample
        self.synapse.insert(sample, self.mol_id)

        if self.verbose:
            print("Removed %f molecules" % sample)
