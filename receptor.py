# Receptor Model
#
# Models a receptor pool of a postsynaptic, to which neurotransmitters from
#     the synapse bind, modifying the membrane potential of the cell.

from math import exp

class Receptor:
    def __init__(self, mol_id, synapse, initial_size,
                    release_time_factor=10, verbose=False):
        """
        Receptors get neurotransmitters from a synapse and release them back
            over time.

        |mol_id| is the identifier for the neurotransmitter to be bound.
        |synapse| is the synapse to retrieve from.
        |initial_size| is the initial size of the receptor pool.
        |release_time_factor| controls the release of neurotransmitter back
            into the synapse.  Higher values increase the rate of release.
        """
        if initial_size > 1.0: raise ValueError
        self.mol_id = mol_id
        self.size = initial_size
        self.release_time_factor = release_time_factor 
        self.synapse = synapse
        self.concentration = 0.0
        self.verbose = verbose

    def step(self, time):
        """
        Runs a time step.
        First, molecules are released.
        Then, molecules are retrieved from the synapse based on a sampled count
            and the size of the receptor pool.
        """
        self.release()
        sample = self.synapse.get(self.mol_id)
        bound = sample * self.size
        self.synapse.remove(self.mol_id, bound)
        self.concentration += bound

    def release(self):
        """
        Releases some neurotransmitters back into the synapse.
        """
        remove = self.concentration / self.release_time_factor
        self.concentration -= remove
        self.synapse.insert(self.mol_id, remove)
        if self.verbose:
            print("Removed %f molecules" % remove)
            print("Receptor: %f" % self.concentration)
