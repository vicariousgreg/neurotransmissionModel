# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synapse.
#
# Release follows strength * (1 - e^(-time_factor * age))

from math import exp
from random import gauss

class Axon:
    def __init__(self, mol_id, synapse, reuptake_size=1.0, baseline_concentration=1.0,
                    release_time_factor=1, replenish_time_factor=1, verbose=False):
        """
        Axon keep track of activation and release neurotransmitters over
            time.

        |mol_id| is the identifier for the neurotransmitter to be released.
        |synapse| is the synapse to release into.
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
        self.synapse = synapse
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

    def step(self, time):
        """
        Runs a time step.
        Molecules are cleared from the synapse every time step.
        The amount cleared depends on the concentrations of molecules
            and their corresponding enzymes.
        Molecules are also replenished based on the concentration available.
        """
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
            difference = gauss(expected - released,0.01)
            mol_count = max(0, min(difference, self.concentration))
            self.concentration -= mol_count
            self.synapse.insert(self.mol_id, mol_count)

            total_released += mol_count

            # Expiration of activity
            if age > self.release_time_factor and difference < 0.000001:
                to_remove.append(i)

            if self.verbose:
                print("Released %f molecules (%d)" % (mol_count, i))
                #print("Total released: %f" % self.potential_released[i])
        #print(total_released)

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
        new_molecules = (self.baseline_concentration - self.concentration) / self.replenish_time_factor
        new_molecules = gauss(new_molecules, 0.01)
        self.concentration += new_molecules
        if self.verbose:
            print("Regenerated %f" % new_molecules)
            print("Axon: %f" % self.concentration)

    def reuptake(self):
        """
        Reuptakes neurotransmitters from the synapse.
        """
        sample = self.synapse.get(self.mol_id)
        reuptaken = sample * self.reuptake_size
        self.synapse.remove(self.mol_id, reuptaken)
        self.concentration += reuptaken
        if self.verbose:
            print("Reuptake %f" % reuptaken)
