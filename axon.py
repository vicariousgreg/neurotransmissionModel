# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synaptic cleft.
#
# Release follows strength * (1 - e^(-time_factor * age))

from math import exp
from sys import maxint

from molecule import Molecules, Transporters
from membrane import TransporterMembrane

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

class Axon(TransporterMembrane):
    def __init__(self, transporter=Transporters.GLUTAMATE, reuptake_rate=1.0,
                    capacity=1.0, release_time_factor=1,
                    replenish_rate=5, environment=False, verbose=None):
        """
        Axon keep track of activation and release neurotransmitters over
            time.

        |transporter| is the type of transporter on the axon.
        |reuptake_rate| is the concentration of reuptake receptors on the
            membrane, and controls the rate of neurotransmitter reuptake.
        |capacity| is the neurotransmitter capacity in the axon vesicles.
        |release_time_factor| controls the release of neurotransmitter over
            time.  Higher values delay release.
        |replenish_rate| controls the regeneration of neurotransmitter 
            over time.  Higher values increase rate of restoration.
        """
        # Initialize as a Transporter Membrane.
        TransporterMembrane.__init__(self, transporter,
            density=reuptake_rate,
            capacity=capacity,
            environment=environment)
        self.verbose = verbose

        # Time factors
        self.replenish_rate = replenish_rate
        self.release_multiple = 5.0 / release_time_factor 

        # Spike generators.
        self.voltage_spikes = []

    def fire(self, voltage, time):
        """
        Fires an action/graded |potential|.
        """
        self.voltage_spikes.append(
            release_generator(self.release_multiple, voltage))

    def release(self, destination):
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
            if difference < 0.000001:
                to_remove.append(i)

            if self.verbose:
                print("Released %f molecules (%d)" % (released, i))

        # Remove expired voltage spikes
        for i in reversed(to_remove):
            del self.voltage_spikes[i]

    def replenish(self):
        """
        Replenishes some neurotransmitters.
        """
        if self.get_native_concentration() >=  self.capacity \
            or self.replenish_rate == 0.0: return

        missing = self.capacity - self.get_native_concentration()
        sample = self.environment.beta(missing, rate=self.replenish_rate)
        self.add_concentration(sample, self.native_mol_id)

        if self.verbose:
            print("Regenerated %f" % sample)
            print("Axon: %f" % self.get_native_concentration())
