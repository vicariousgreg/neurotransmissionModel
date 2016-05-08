# Environment
#
# When components with pools are created, they should be passed an environment
#     and register with a pool_id.
#
# The batch environment holds concentrations of neurotransmitters for pools.
# An array is kept for previous and next concentrations to avoid race
#     race conditions.  When a timestep is run, the buffers shift.
# Concentrations are retrieved from prev_concentrations
#     and set to next_concentrations.

from random import betavariate

def betav(maximum, noise=0.5, rate=1.0):
    if rate < 0.0 or noise < 0.0: raise ValueError
    ratio = 1/(0.0001+rate)
    a = 1.0+(100.0*(1.0-noise))
    b = ratio * a
    return maximum*(betavariate(a,b))

class Environment:
    def __init__(self, noise=0.5):
        self.concentrations = []
        def beta(maximum, rate=1.0):
            return betav(maximum, noise=noise, rate=rate)
        self.beta = beta

    def create_pool(self, baseline_concentration):
        pool_id = len(self.concentrations)
        self.concentrations.append(baseline_concentration)
        return pool_id

    def get_concentration(self, pool_id):
        return self.concentrations[pool_id]

    def set_concentration(self, pool_id, new_concentration):
        self.concentrations[pool_id] = new_concentration

    def add_concentration(self, pool_id, molecules):
        self.concentrations[pool_id] += molecules

    def remove_concentration(self, pool_id, molecules):
        self.concentrations[pool_id] -= molecules

    def step(self): pass

class BatchEnvironment:
    def __init__(self, noise=0.5):
        self.prev_concentrations = []
        self.next_concentrations = []
        def beta(maximum, rate=1.0):
            return betav(maximum, noise=noise, rate=rate)
        self.beta = beta

    def create_pool(self, baseline_concentration):
        pool_id = len(self.prev_concentrations)
        self.prev_concentrations.append(baseline_concentration)
        self.next_concentrations.append(baseline_concentration)
        return pool_id

    def get_concentration(self, pool_id):
        return self.prev_concentrations[pool_id]

    def set_concentration(self, pool_id, new_concentration):
        self.next_concentrations[pool_id] = new_concentration

    def add_concentration(self, pool_id, molecules):
        self.next_concentrations[pool_id] += molecules

    def remove_concentration(self, pool_id, molecules):
        self.next_concentrations[pool_id] -= molecules
        self.next_concentrations[pool_id] = \
            max(0.0, self.next_concentrations[pool_id])

    def step(self):
        for i in xrange(len(self.prev_concentrations)):
            self.prev_concentrations[i]=self.next_concentrations[i]
