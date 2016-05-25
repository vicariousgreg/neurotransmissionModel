# Environments
#
# Any values that are accessed by more than one entity should go in the
#     environment.  Entities should register with an env_id.
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

class Environment:
    def __init__(self, noise=0.0):
        def beta(maximum, rate=1.0):
            return betav(maximum, noise=noise, rate=rate)
        self.beta = beta

        self.prev_values = []
        self.next_values = []
        self.dirty = True
        self.records = dict()
        self.spikes = dict()

    def get_record(self, env_id, spikes=False):
        if spikes: return self.spikes[env_id]
        else: return self.records[env_id]

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
        self.dirty = True
        self.next_values[env_id] = new_voltage

    def adjust(self, env_id, delta):
        self.dirty = True
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
                self.spikes[env_id] += 1

        if self.dirty:
            self.dirty = False
            for i in xrange(len(self.prev_values)):
                self.prev_values[i]=self.next_values[i]
            return False
        else: return True
