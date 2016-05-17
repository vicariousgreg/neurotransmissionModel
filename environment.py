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

from random import betavariate

def betav(maximum, noise=0.5, rate=1.0):
    if rate < 0.0 or noise < 0.0: raise ValueError
    ratio = 1/(0.0001+rate)
    a = 1.0+(100.0*(1.0-noise))
    b = ratio * a
    return maximum*(betavariate(a,b))

class SynapseEnvironment:
    def __init__(self, noise=0.0):
        self.prev_concentrations = []
        self.next_concentrations = []
        def beta(maximum, rate=1.0):
            return betav(maximum, noise=noise, rate=rate)
        self.beta = beta
        self.dirty = False

    def register(self, baseline_concentration):
        pool_id = len(self.prev_concentrations)
        self.prev_concentrations.append(baseline_concentration)
        self.next_concentrations.append(baseline_concentration)
        return pool_id

    def get_concentration(self, pool_id):
        return self.prev_concentrations[pool_id]

    def set_concentration(self, pool_id, new_concentration):
        self.dirty = True
        self.next_concentrations[pool_id] = new_concentration

    def add_concentration(self, pool_id, molecules):
        self.dirty = True
        self.next_concentrations[pool_id] += molecules

    def remove_concentration(self, pool_id, molecules):
        self.dirty = True
        self.next_concentrations[pool_id] -= molecules
        self.next_concentrations[pool_id] = \
            max(0.0, self.next_concentrations[pool_id])

    def step(self):
        """
        Cycles the environment.
        Returns whether the environment is stable (not dirty, no changes)
        """
        if self.dirty:
            self.dirty = False
            for i in xrange(len(self.prev_concentrations)):
                self.prev_concentrations[i]=self.next_concentrations[i]
            return False
        else: return True

class NeuronEnvironment:
    def __init__(self, noise=0.0):
        self.prev_voltages = []
        self.next_voltages = []
        def beta(maximum, rate=1.0):
            return betav(maximum, noise=noise, rate=rate)
        self.beta = beta
        self.dirty = False

    def register(self, baseline_voltage=0.0):
        neuron_id = len(self.prev_voltages)
        self.prev_voltages.append(baseline_voltage)
        self.next_voltages.append(baseline_voltage)
        return neuron_id

    def get_voltage(self, neuron_id):
        return self.prev_voltages[neuron_id]

    def set_voltage(self, neuron_id, new_voltage):
        self.dirty = True
        self.next_voltages[neuron_id] = new_voltage

    def adjust_voltage(self, neuron_id, delta):
        self.dirty = True
        self.next_voltages[neuron_id] += delta

    def step(self):
        """
        Cycles the environment.
        Returns whether the environment is stable (not dirty, no changes)
        """
        if self.dirty:
            self.dirty = False
            for i in xrange(len(self.prev_voltages)):
                self.prev_voltages[i]=self.next_voltages[i]
            return False
        else: return True
