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

class Environment:
    def __init__(self):
        self.concentrations = []

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

    def step(self, time): pass

class BatchEnvironment:
    def __init__(self):
        self.prev_concentrations = []
        self.next_concentrations = []

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

    def step(self, time):
        for i in xrange(len(self.prev_concentrations)):
            self.prev_concentrations[i]=self.next_concentrations[i]

