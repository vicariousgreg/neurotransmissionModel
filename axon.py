# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synaptic cleft.
#
# Release follows (strength * (1 - e^(-time_factor * age)))

from sys import maxint

from scipy.stats import erlang

from molecule import Transporters
from membrane import TransporterMembrane

er = erlang(2)
erlang_cache = dict()

def get_prob(release_multiple, x):
    return erlang_cache[release_multiple][x]

def fill_cache(release_multiple):
    if release_multiple in erlang_cache: return

    erlang_cache[release_multiple] = []
    prev = 0.0

    for x in xrange(maxint):
        curr = er.cdf(release_multiple*x)
        diff = curr - prev
        prev = curr
        erlang_cache[release_multiple].append(diff)
        if diff != 0.0 and diff < 0.000001:
            break

def release_generator(release_multiple, strength):
    """
    Creates a generator for neurotransmitter spike over time steps.
    |release_multiple| comes from the Axon, and specifies the time course
        over which the spike is stretched (see Axon)
    |strength| is the strength of the spike
    """
    fill_cache(release_multiple)
    for x in xrange(maxint):
        yield strength*get_prob(release_multiple, x)

class Axon(TransporterMembrane):
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
        # Initialize as pool cluster
        TransporterMembrane.__init__(self, transporter, reuptake_rate, capacity, environment)

        # Time factors
        self.replenish_rate = replenish_rate
        self.release_multiple = 10.0 / release_time_factor 

        # Spike generators.
        self.voltage_spikes = []

        self.verbose = verbose

    def fire(self, voltage):
        """
        Triggers the release of neurotransmitter over time.
        The amount to be released is determined by the input |voltage|.
        """
        if voltage == 0.0: return
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
            released = min(self.get_native_concentration(),
                self.environment.beta(difference, rate=1))

            # Transfer concentration.
            self.remove_concentration(released, self.native_mol_id)
            destination.add_concentration(released, mol_id=self.native_mol_id)

            # Expiration of activity
            if difference != 0.0 and difference < 0.000001: to_remove.append(i)

            if self.verbose: print("Released %f molecules (%d)" % (released, i))

        # Remove expired voltage spikes
        for i in reversed(to_remove):
            del self.voltage_spikes[i]

    def replenish(self):
        """
        Replenishes neurotransmitters if the axon is not at capacity.
        """
        native_concentration = self.get_native_concentration()
        if native_concentration >=  self.capacity \
            or self.replenish_rate == 0.0: return

        missing = self.capacity - native_concentration
        sample = self.environment.beta(missing, rate=self.replenish_rate)
        self.add_concentration(sample, self.native_mol_id)

        if self.verbose:
            print("Regenerated %f" % sample)
            print("Axon: %f" % self.get_concentration(self.native_mol_id))
