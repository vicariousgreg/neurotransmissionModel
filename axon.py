# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synapse.
#
# Release follows strength * (1 - e^(-time_factor * age))

from math import exp
from stochastic import beta

from molecule import Molecules
from pool import Pool
from membrane import stochastic_bind

class Axon(Pool):
    def __init__(self, mol_id=Molecules.GLUTAMATE, reuptake_rate=1.0,
                    capacity=1.0, release_time_factor=1,
                    replenish_rate=5, verbose=False):
        """
        Axon keep track of activation and release neurotransmitters over
            time.

        |mol_id| is the identifier for the neurotransmitter to be released.
        |reuptake_rate| is the concentration of reuptake receptors.
        |initial_size| is the maximum concentration of neurotransmitter.
        |release_time_factor| controls the release of neurotransmitter over
            time.  Higher values delay release.
        |replenish_rate| controls the regeneration of neurotransmitter 
            over time.  Higher values increase rate of restoration.
        """
        # Initialize as a membrane.
        super(Axon, self).__init__(baseline_concentration=capacity)

        # Cell attributes
        self.mol_id = mol_id
        self.capacity = capacity
        self.size = reuptake_rate
        self.verbose = verbose

        # Time factors
        self.replenish_rate = replenish_rate
        self.release_time_factor = release_time_factor 
        self.release_multiple = 5.0 / release_time_factor 

        # Records of activity
        self.potential_strengths = []
        self.potential_times = []
        self.potential_released = []

    def get_available_spots(self):
        return self.size

    def step(self, time):
        """
        Runs a time step.
        Molecules are cleared from the synapse every time step.
        The amount cleared depends on the concentrations of molecules
            and their corresponding enzymes.
        Molecules are also replenished based on the concentration available.
        """
        if self.get_concentration() < self.capacity:
            if self.replenish_rate > 0.0: self.replenish()
        to_remove = []

        for i in xrange(len(self.potential_times)):
            strength = self.potential_strengths[i]
            time_tag = self.potential_times[i]
            already_released = self.potential_released[i]

            # Calculate the age and determine the expected number of
            #     released neurotransmitters.
            age = time - time_tag
            expected = strength*(1 - exp(self.release_multiple * -float(age)))
            difference = expected - already_released

            # Determine how many molecules to actually release.
            mol_count = beta(difference, rate=2)
            mol_count = min(mol_count, self.get_concentration())
            self.remove_concentration(mol_count)
            if self.destination:
                self.destination.add_concentration(mol_count, mol_id=self.mol_id)

            # Decrement released
            self.potential_released[i] = self.potential_released[i] + mol_count

            # Expiration of activity
            if age > self.release_time_factor and difference < 0.000001:
                to_remove.append(i)

            if self.verbose:
                print("Released %f molecules (%d)" % (mol_count, i))

        # Remove expired activations
        for i in reversed(to_remove):
            del self.potential_strengths[i]
            del self.potential_times[i]
            del self.potential_released[i]

    def fire(self, potential, time):
        """
        Fires an action/graded |potential|.
        """
        if potential > 1.0: raise ValueError

        self.potential_strengths.append(potential)
        self.potential_times.append(time)
        self.potential_released.append(0.0)

    def replenish(self):
        """
        Replenishes some neurotransmitters.
        """
        missing = self.capacity - self.get_concentration()
        sample = beta(missing, rate=self.replenish_rate)
        self.add_concentration(sample)
        if self.verbose:
            print("Regenerated %f" % sample)
            print("Axon: %f" % self.get_concentration())
