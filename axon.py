# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synapse.
#
# Release follows strength * (1 - e^(-time_factor * age))

from math import exp
from random import gauss, betavariate

from molecule import Molecules

class Axon:
    def __init__(self, mol_id=Molecules.GLUTAMATE, reuptake_size=1.0, baseline_concentration=1.0,
                    release_time_factor=1, replenish_time_factor=5, verbose=False):
        """
        Axon keep track of activation and release neurotransmitters over
            time.

        |mol_id| is the identifier for the neurotransmitter to be released.
        |reuptake_size| is the number of reuptake receptors.
        |baseline_concentration| is the maximum concentration of
            neurotransmitter.
        |release_time_factor| controls the release of neurotransmitter over
            time.  Higher values delay release.
        |replenish_time_factor| controls the regeneration of neurotransmitter 
            over time.  Higher values increase rate of restoration.
        """
        # Cell attributes
        self.mol_id = mol_id
        self.synapse = None
        self.reuptake_size = reuptake_size
        self.verbose = verbose

        # Concentration
        self.baseline_concentration = baseline_concentration
        self.concentration = baseline_concentration

        # Time factors
        self.replenish_time_factor = replenish_time_factor
        self.release_time_factor = release_time_factor 
        self.release_multiple = 5.0 / release_time_factor 

        # Records of activity
        self.potential_strengths = []
        self.potential_times = []
        self.potential_released = []

    def set_synapse(self, synapse):
        """
        Connects the axon to a synapse.
        """
        self.synapse = synapse

    def step(self, time):
        """
        Runs a time step.
        Molecules are cleared from the synapse every time step.
        The amount cleared depends on the concentrations of molecules
            and their corresponding enzymes.
        Molecules are also replenished based on the concentration available.
        """
        if self.concentration < self.baseline_concentration:
            self.reuptake()
            self.replenish()
        to_remove = []
        total_released = 0.0

        for i in xrange(len(self.potential_times)):
            strength = self.potential_strengths[i]
            time_tag = self.potential_times[i]
            released = self.potential_released[i]

            # Calculate the age and determine the expected number of
            #     released neurotransmitters.
            age = time - time_tag
            expected = strength*(1 - exp(self.release_multiple * -float(age)))
            self.potential_released[i] = expected

            # Determine how many molecules to actually release.
            difference = expected - released
            difference = min(self.concentration, difference, difference*(1-betavariate(2,20)))

            mol_count = max(0, difference)
            self.concentration -= mol_count
            self.synapse.insert(self.mol_id, mol_count)

            total_released += mol_count

            # Expiration of activity
            if age > self.release_time_factor and difference < 0.000001:
                to_remove.append(i)

            if self.verbose:
                print("Released %f molecules (%d)" % (mol_count, i))
                #print("Total released: %f" % self.potential_released[i])
        #if self.verbose: print(total_released)

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
        missing = self.baseline_concentration - self.concentration
        sample = min(missing, missing*(betavariate(2,2+self.replenish_time_factor)))
        self.concentration += sample
        if self.verbose:
            print("Regenerated %f" % sample)
            print("Axon: %f" % self.concentration)

    def reuptake(self):
        """
        Reuptakes neurotransmitters from the synapse.
        """
        # Check available molecules
        available = self.synapse.get(self.mol_id)
        if available <= 0: return

        # Sample available molecules
        sample = min(1.0, available, available*(1-betavariate(2,20)))
        reuptaken = (self.baseline_concentration-self.concentration) * sample * self.reuptake_size

        if self.verbose:
            print("Reuptake %f" % reuptaken)

        # Bind sampled molecules
        self.synapse.remove(self.mol_id, reuptaken)
        self.concentration += reuptaken
