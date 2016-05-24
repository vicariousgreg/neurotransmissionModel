# Environments
#
# Synapse Environment:
#     When components with pools are created, they should be passed a 
#         synapse environment and register with a pool_id.
#     The environment holds concentrations of neurotransmitters for pools.
#
# Neuron Environment:
#     When neurons are created, they should be passed a neuron environment
#         and register their soma with an environment_id.
#     The environment holds the voltages of neuron somas.
#     After registering, the neuron should stabilize its voltage and set it.
#
# An array is kept for previous and next values to avoid race conditions.
#     When a timestep is run, the buffers shift.
# Values are retrieved from the pervious array and set to the next array.
#
# All concentration/voltage and dirty values are thread safe.
# To speed them up, the locks are disabled.  There should be no instances of
#     multiple threads trying to change a value.

from random import betavariate
from multiprocessing import Value, Array, Manager
manager = Manager()

def betav(maximum, noise=0.5, rate=1.0):
    if rate < 0.0 or noise < 0.0: raise ValueError
    ratio = 1/(0.0001+rate)
    a = 1.0+(100.0*(1.0-noise))
    b = ratio * a
    return maximum*(betavariate(a,b))

class Environment:
    def __init__(self, noise=0.0, multithreaded=False):
        def beta(maximum, rate=1.0):
            return betav(maximum, noise=noise, rate=rate)
        self.beta = beta
        self.multithreaded = multithreaded

        self.prev_values = []
        self.next_values = []
        self.dirty = Value('b', True, lock=False)
        self.records = dict()
        self.spikes = dict()

    def initialize(self):
        if self.multithreaded:
            # Create thread safe arrays.
            self.prev_values = Array('d', self.prev_values, lock=False)
            self.next_values = Array('d', self.next_values, lock=False)

            for key in self.records:
                self.records[key] = manager.list()
            for key in self.spikes:
                self.spikes[key] = Value('i', 0, lock=False)

    def register(self, initial=0.0, record=False, spiking=False):
        env_id = len(self.prev_values)
        self.prev_values.append(initial)
        self.next_values.append(initial)
        if record:
            self.records[env_id] = []
            if spiking:
                self.spikes[env_id] = 0
        return env_id

    def get(self, env_id):
        return self.prev_values[env_id]

    def set(self, env_id, new_voltage):
        self.dirty.value = True
        self.next_values[env_id] = new_voltage

    def adjust(self, env_id, delta):
        self.dirty.value = True
        self.next_values[env_id] += delta

    def step(self):
        """
        Cycles the environment.
        Returns whether the environment is stable (not dirty, no changes)
        """
        # Record any env_ids that have been set to record.
        for env_id in self.records:
            self.records[env_id].append(self.prev_values[env_id])
        for env_id in self.spikes:
            if self.prev_values[env_id] >= 30.0:
                if self.multithreaded:
                    self.spikes[env_id].value += 1
                else:
                    self.spikes[env_id] += 1

        if self.dirty.value:
            self.dirty.value = False
            for i in xrange(len(self.prev_values)):
                self.prev_values[i]=self.next_values[i]
            return False
        else: return True
