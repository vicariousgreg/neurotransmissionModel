# Simple Synapse
#
# The simple synapse does not simulate the axon, synaptic cleft, or dendrite.
# Instead, it simply takes a voltage from the presynaptic neuron and provides
#     a means of activating the postsynaptic neuron.
# It shares an interface with ChemicalSynapse, and is thus interchangeable
#     with it.

from molecule import Receptors
from collections import deque
from sys import maxint
from scipy.stats import erlang

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

class SimpleSynapse:
    def __init__(self, postsynaptic_id=None, receptor=Receptors.AMPA,
                    spiking=True, delay=0, strength=1, environment=None,
                    verbose=False):
        """
        """
        self.postsynaptic_id = postsynaptic_id
        self.receptor = receptor
        self.delay = delay
        self.strength = strength
        self.environment = environment
        self.verbose = verbose
        self.env_id = environment.register(0.0)

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

        return self.release(voltage)

    def activate_dendrites(self, neuron):
        self.receptor.activation_function(self.strength,
            self.environment.get(self.env_id),
            neuron)

    def release(self, voltage):
        """
        Releases neurochemical into the synaptic cleft.
        Returns whether the axon is stable (no release).
        """
        # Determine how many molecules to actually release.
        # If none are to be released, return True (indicating stability)
        released = self.release_function(voltage)
        if released == 0.0:
            return True
        else:
            if self.verbose:
                print("Synapse transmit %f" % released)
            self.environment.set(self.env_id, released)
            return False

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
        threshold = -150.0
        maximum = -82.0

        # If the voltage is too low, don't release.
        if voltage < threshold: return 0.0
        # Otherwise, compute release based on voltage.
        else:
            voltage = min(maximum, voltage)
            return (voltage - threshold) / (maximum - threshold)
