# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synaptic cleft.
#
# Release follows (strength * (1 - e^(-time_factor * age)))

from math import exp
from sys import maxint

from molecule import Transporters
from pool_cluster import PoolCluster

def release_generator(release_multiple, strength):
    """
    Creates a generator for neurotransmitter spike over time steps.
    |release_multiple| comes from the Axon, and specifies the time course
        over which the spike is stretched (see Axon)
    |strength| is the strength of the spike
    """
    prev = 0.0
    for x in xrange(1,maxint):
        curr = strength*(1.0 - exp(release_multiple * -float(x)))
        diff = curr - prev
        prev = curr
        yield diff

class Axon(PoolCluster):
    def __init__(self, transporter=Transporters.GLUTAMATE, reuptake_rate=1.0,
                    capacity=1.0, release_time_factor=1,
                    replenish_rate=5, environment=False, verbose=False):
        """
        Axons keep track of activation and release neurotransmitters over
            time.  Neurotransmitters are regenerated via reuptake and
            replenishing.

        |transporter| is the type of transporter on the axon membrane.
        |reuptake_rate| is the concentration of reuptake receptors on the
            membrane, and controls the rate of neurotransmitter reuptake.
        |capacity| is the neurotransmitter capacity in the axon vesicles.
        |release_time_factor| controls the release of neurotransmitter over
            time.  Higher values delay release.
        |replenish_rate| controls the regeneration of neurotransmitter 
            over time.  Higher values increase rate of restoration.
        """
        self.protein = transporter
        self.native_mol_id = transporter.native_mol_id
        self.density = reuptake_rate
        self.capacity = capacity
        self.affinities = transporter.affinities

        # Initialize as pool cluster
        concentrations = dict([(mol_id, 0.0) for mol_id in transporter.reuptake_inhibitors])
        concentrations[self.native_mol_id] = capacity
        PoolCluster.__init__(self, concentrations, environment)

        # Time factors
        self.replenish_rate = replenish_rate
        self.release_multiple = 5.0 / release_time_factor 

        # Spike generators.
        self.voltage_spikes = []

        self.verbose = verbose

    def get_available_proteins(self, mol_id):
        if mol_id == self.native_mol_id:
            return min(self.density, self.capacity - self.get_concentration(self.native_mol_id))
        else:
            return self.density

    def fire(self, voltage):
        """
        Triggers the release of neurotransmitter over time.
        The amount to be released is determined by the input |voltage|.
        """
        self.voltage_spikes.append(
            release_generator(self.release_multiple, voltage))

    def release(self, destination):
        """
        Releases neurotransmitters according to the history of activity.

        Each fire() call creates a generator for neurotransmitter release that
            follows a (1-e^-x) pattern.  Activations stack on top of one
            another, and they must thus be iterated over.  Once the amount of
            neurotransmitter being released from a particular activation drops
            below a very low threshold, that activation is removed from the
            history to save computation time.  This limits the total number of
            activations to be considered during a timestep.
        """
        to_remove = []

        for i,generator in enumerate(self.voltage_spikes):
            difference = next(generator)

            # Determine how many molecules to actually release.
            released = min(self.get_concentration(self.native_mol_id),
                self.environment.beta(difference, rate=1))

            # Transfer concentration.
            self.remove_concentration(released, self.native_mol_id)
            destination.add_concentration(released, mol_id=self.native_mol_id)

            # Expiration of activity
            if difference < 0.000001: to_remove.append(i)

            if self.verbose: print("Released %f molecules (%d)" % (released, i))

        # Remove expired voltage spikes
        for i in reversed(to_remove):
            del self.voltage_spikes[i]

    def replenish(self):
        """
        Replenishes neurotransmitters if the axon is not at capacity.
        """
        native_concentration = self.get_concentration(self.native_mol_id)
        if native_concentration >=  self.capacity \
            or self.replenish_rate == 0.0: return

        missing = self.capacity - native_concentration
        sample = self.environment.beta(missing, rate=self.replenish_rate)
        self.add_concentration(sample, self.native_mol_id)

        if self.verbose:
            print("Regenerated %f" % sample)
            print("Axon: %f" % self.get_concentration(self.native_mol_id))
