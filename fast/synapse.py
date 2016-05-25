# Simple Synapse
#
# The simple synapse does not simulate the axon, synaptic cleft, or dendrite.
# Instead, it simply takes a voltage from the presynaptic neuron and provides
#     a means of activating the postsynaptic neuron.

from receptor import epsp
from collections import deque

class SpikingSynapse:
    def __init__(self, receptor=epsp, delay=0, strength=1, environment=None, verbose=False):
        self.receptor = receptor
        self.delay = delay
        self.strength = strength
        self.environment = environment
        self.verbose = verbose
        self.env_id = environment.register(0.0)

        self.prev = False
        if delay:
            self.delay_queue = deque()
            for _ in xrange(delay):
                self.delay_queue.appendleft(-70.0)
        else:
            self.delay_queue = None

    def activate_dendrites(self, neuron):
        self.receptor(self.strength,
            self.environment.get(self.env_id),
            neuron)

    def step(self, voltage):
        # If there is a delay, use the queue.
        try:
            self.delay_queue.appendleft(voltage)
            # Remove voltage from queue.
            self.release(self.delay_queue.pop())
        except AttributeError: 
            self.release(voltage)

    def release(self, voltage):
        if voltage > 30:
            self.environment.set(self.env_id, 1.0)
            self.prev = True
            if self.verbose: print("Spiking synapse transmit")
        elif self.prev:
            self.environment.set(self.env_id, 0.0)
            self.prev = False

class GradedSynapse:
    def __init__(self, receptor=epsp, delay=0, strength=1, environment=None, verbose=False):
        self.receptor = receptor
        self.delay = delay
        self.strength = strength
        self.environment = environment
        self.verbose = verbose
        self.env_id = environment.register(0.0)

        if delay:
            self.delay_queue = deque()
            for _ in xrange(delay):
                self.delay_queue.appendleft(-70.0)
        else:
            self.delay_queue = None

    def activate_dendrites(self, neuron):
        self.receptor(self.strength,
            self.environment.get(self.env_id),
            neuron)

    def step(self, voltage):
        # If there is a delay, use the queue.
        try:
            self.delay_queue.appendleft(voltage)
            # Remove voltage from queue.
            self.release(self.delay_queue.pop())
        except AttributeError: self.release(voltage)

    def release(self, voltage):
        # Determine how many molecules to actually release.
        threshold = -150.0
        maximum = -82.0

        # If the voltage is too low, don't release.
        if voltage < threshold: released = 0.0
        # Otherwise, compute release based on voltage.
        else:
            voltage = min(maximum, voltage)
            released = (voltage - threshold) / (maximum - threshold)

        self.environment.set(self.env_id, released)
        if self.verbose:
            if released > 0.0: print("Graded synapse transmit %f" % released)
