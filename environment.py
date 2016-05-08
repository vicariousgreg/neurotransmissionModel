# Environment
#
# When components with pools are created, they should be passed an environment
#     and register with a pool_id.
#
# The batch environment holds concentrations of neurotransmitters for pools.
# An array is kept for previous and next concentrations to avoid race
#     race conditions.  When a timestep is run, the buffers flip.
# Concentrations are retrieved from prev_concentrations
#     and set to next_concentrations.

import stochastic

class Environment:
    def __init__(self, noise=0.5):
        self.concentrations = []
        def beta(maximum, rate=1.0):
            return stochastic.beta(maximum, noise=noise, rate=rate)
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

    def get_id(self):
        identity = len(self.concentrations)
        self.concentrations.append(0.0)
        return identity

    def step(self): pass

class BatchEnvironment:
    def __init__(self, noise=0.5):
        self.prev_concentrations = []
        self.next_concentrations = []
        def beta(maximum, rate=1.0):
            return stochastic.beta(maximum, noise=noise, rate=rate)
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

    def get_id(self):
        identity = len(self.prev_concentrations)
        self.next_concentrations.append(0.0)
        self.prev_concentrations.append(0.0)
        return identity

    def step(self):
        for i in xrange(len(self.prev_concentrations)):
            self.prev_concentrations[i]=self.next_concentrations[i]

