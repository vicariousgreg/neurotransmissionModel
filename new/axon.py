# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synaptic cleft.

from collections import deque
from sys import maxint
from scipy.stats import erlang
from molecule import Transporters

er = erlang(2)

def erlang_generator():
    """
    Creates an erlang generator.
    """
    prev = 0.0

    for x in xrange(1, maxint):
        curr = er.cdf(x)
        diff = curr - prev
        if diff < 0.001: break
        prev = curr
        yield diff

class Axon:
    def __init__(self, synaptic_cleft, transporter=Transporters.GLUTAMATE,
                        reuptake_rate=0.5, capacity=1.0, replenish_rate=0.1,
                        delay=0, spiking=True, verbose=False):
        """
        Axons keep track of activation and release neurotransmitters over
            time.  Neurotransmitters are regenerated via reuptake and
            replenishing.

        |synaptic_cleft| is the synaptic cleft this axon releases into.
        |transporter| is the type of transporter on the axon membrane.
        |reuptake_rate| is the concentration of reuptake receptors on the
            membrane, and controls the rate of neurotransmitter reuptake.
        |capacity| is the neurotransmitter capacity in the axon vesicles.
        |replenish_rate| controls the regeneration of neurotransmitter 
            over time.  Higher values increase rate of restoration.
        |delay| specifies how long it takes the axon to respond, and sets
            the size of a queue.

        Axons respond directly to the voltage of the neuron, and have both a
            threshold minimum voltage for activity, and a ceiling for voltage.
        Voltage determines the rate of neurochemical release according to a
            particular release function.
        Release pulls from a pool tracked by self.concentration.  This pool is
            also automatically regenerated according to the |replenish rate|,
            and externally via reuptake from the synaptic cleft according to
            the |reuptake rate|.  This interaction is mediated by the synaptic
            cleft itself, and depends on the |transporter| protein on the axon.
        """
        self.synaptic_cleft = synaptic_cleft
        self.protein = transporter
        self.affinities = transporter.affinities
        self.native_mol_id = transporter.native_mol_id

        self.capacity = capacity
        self.density = reuptake_rate
        self.concentration = capacity
        self.replenish_rate = replenish_rate

        if spiking:
            self.release_generator = None
            self.release_function = self.spike_release
        else:
            self.release_function = self.graded_release

        if delay:
            self.delay_queue = deque()
            for _ in xrange(delay):
                self.delay_queue.appendleft(-70.0)
        else:
            self.delay_queue = None

        self.verbose = verbose

    def get_concentration(self):
        return self.concentration

    def set_concentration(self, new_concentration):
        self.concentration = new_concentration

    def add_concentration(self, delta):
        self.concentration += delta

    def remove_concentration(self, delta):
        self.concentration -= delta

    def step(self, voltage):
        """
        Cycles the axon.
        """
        # If there is a delay, use the queue.
        try:
            self.delay_queue.appendleft(voltage)
            # Remove voltage from queue.
            voltage = self.delay_queue.pop()
        except AttributeError: pass

        stable = self.replenish()
        stable &= self.release(voltage)
        return self.synaptic_cleft.step() & stable

    def spike_release(self, voltage):
        # If the voltage exceeds the threshold for spiking, create a release
        #     generator (erlang distribution).  Return the first call.
        if voltage > 30:
            gen = erlang_generator()
            self.release_generator = gen
            return next(gen)

        # Otherwise, attempt to access the release generator, and return the
        #     results of the next() call.  If that fails, the release is
        #     complete for the previous spike, and 0.0 can be returned.
        else:
            try:
                return next(self.release_generator)
            except TypeError: return 0.0
            except StopIteration:
                self.release_generator = None
                return 0.0

    def graded_release(self, voltage):
        # If the voltage is too low, don't release.
        if voltage < -70.0: return 0.0
        # Otherwise, compute release based on voltage.
        else:
            voltage = min(-40.0, voltage)
            return (voltage + 70.0) / 30.0

    def release(self, voltage):
        """
        Releases neurochemical into the synaptic cleft.
        Returns whether the axon is stable (no release).
        """
        # Determine how many molecules to actually release.
        # If none are to be released, return True (indicating stability)
        released = min(self.concentration, self.release_function(voltage))
        if released == 0.0:
            return True
        else:
            # Remove concentration.
            self.remove_concentration(released)
            if self.verbose:
                print("Axon release %f (%f / %f)" %
                    (released, self.get_concentration(), self.capacity))
            self.synaptic_cleft.add_concentration(released, self.native_mol_id)
            return False

    def replenish(self):
        """
        Replenishes neurotransmitters if the axon is not at capacity.
        Returns whether the axon is stable (at capacity).
        """
        # Determine concentration to replenish
        # Because of the asymptotic nature of regeneration, once the difference
        #     becomes negligible, simply fill to capacity to save time.
        missing = self.capacity - self.get_concentration()
        if missing <= 0.0 or self.replenish_rate == 0.0: return True
        elif missing < 0.001:
            self.set_concentration(self.capacity)
            return True
        else:
            sample = self.replenish_rate * missing
            self.add_concentration(sample)

        if self.verbose:
            print("Axon regen %f (%f / %f)" %
                (sample, self.get_concentration(), self.capacity))

        return False
