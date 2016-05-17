# Environments
#
# Synapse Environment:
#     When components with pools are created, they should be passed a 
#         synapse environment and register with a pool_id.
#     The environment holds concentrations of neurotransmitters for pools.
#
# Neuron Environment:
#     When neurons are created, they should be passed a neuron environment
#         and register their soma with a neuron_id.
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
from multiprocessing import Value, Array

def betav(maximum, noise=0.5, rate=1.0):
    if rate < 0.0 or noise < 0.0: raise ValueError
    ratio = 1/(0.0001+rate)
    a = 1.0+(100.0*(1.0-noise))
    b = ratio * a
    return maximum*(betavariate(a,b))

class SynapseEnvironment:
    def __init__(self, noise=0.0):
        def beta(maximum, rate=1.0):
            return betav(maximum, noise=noise, rate=rate)
        self.beta = beta

        self.prev_concentrations = Array('d', [], lock=False)
        self.next_concentrations = Array('d', [], lock=False)
        self.dirty = Value('b', False, lock=False)

    def register(self, baseline_concentration):
        pool_id = len(self.prev_concentrations)
        self.prev_concentrations = Array('d',
            list(self.prev_concentrations) + [baseline_concentration],
            lock=False)
        self.next_concentrations = Array('d',
            list(self.next_concentrations) + [baseline_concentration],
            lock=False)
        return pool_id

    def get_concentration(self, pool_id):
        return self.prev_concentrations[pool_id]

    def set_concentration(self, pool_id, new_concentration):
        self.dirty.value = True
        self.next_concentrations[pool_id] = new_concentration

    def add_concentration(self, pool_id, molecules):
        self.dirty.value = True
        self.next_concentrations[pool_id] += molecules

    def remove_concentration(self, pool_id, molecules):
        self.dirty.value = True
        self.next_concentrations[pool_id] -= molecules
        self.next_concentrations[pool_id] = \
            max(0.0, self.next_concentrations[pool_id])

    def step(self):
        """
        Cycles the environment.
        Returns whether the environment is stable (not dirty, no changes)
        """
        if self.dirty.value:
            self.dirty.value = False
            for i in xrange(len(self.prev_concentrations)):
                self.prev_concentrations[i]=self.next_concentrations[i]
            return False
        else: return True

class NeuronEnvironment:
    def __init__(self, noise=0.0):
        def beta(maximum, rate=1.0):
            return betav(maximum, noise=noise, rate=rate)
        self.beta = beta

        self.prev_voltages = Array('d', [], lock=False)
        self.next_voltages = Array('d', [], lock=False)
        self.dirty = Value('b', False, lock=False)

    def register(self, baseline_voltage=0.0):
        neuron_id = len(self.prev_voltages)
        self.prev_voltages = Array('d',
            list(self.prev_voltages) + [baseline_voltage],
            lock=False)
        self.next_voltages = Array('d',
            list(self.next_voltages) + [baseline_voltage],
            lock=False)
        return neuron_id

    def get_voltage(self, neuron_id):
        return self.prev_voltages[neuron_id]

    def set_voltage(self, neuron_id, new_voltage):
        self.dirty.value = True
        self.next_voltages[neuron_id] = new_voltage

    def adjust_voltage(self, neuron_id, delta):
        self.dirty.value = True
        self.next_voltages[neuron_id] += delta

    def step(self):
        """
        Cycles the environment.
        Returns whether the environment is stable (not dirty, no changes)
        """
        if self.dirty.value:
            self.dirty.value = False
            for i in xrange(len(self.prev_voltages)):
                self.prev_voltages[i]=self.next_voltages[i]
            return False
        else: return True
