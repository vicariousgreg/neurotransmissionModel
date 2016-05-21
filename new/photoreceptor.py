# Photoreceptor Soma Model
#
# Photoreceptors do not generate action potentials.  Instead, they have a base
#     current that triggers the release of glutamate in the dark.  With light
#     activation, ion conductance is reduced, and less glutamate is released.
#     The end result is high release in the dark, low release in the light.

class PhotoreceptorSoma:
    def __init__(self, environment=None, resolution=100):
        self.current = 0
        self.environment = environment
        self.stable_voltage = -82.6556443707
        self.env_id = environment.register(self.stable_voltage)
        self.resolution = resolution
        self.time_coefficient = 1.0 / resolution

        self.firing = False
        self.light_level = 0.0

    def get_voltage(self):
        """
        NEEDS TO BE THREAD SAFE
        """
        return self.environment.get(self.env_id)

    def set_voltage(self, v):
        """
        NEEDS TO BE THREAD SAFE
        """
        self.environment.set(self.env_id, v)

    def adjust(self, old_current, new_current):
        return old_current + ((new_current - old_current) / 2)

    def step(self, current=0.0):
        old_current = self.current
        current = self.adjust(old_current, current)
        self.current = current

        old_voltage = self.get_voltage()
        voltage = old_voltage

        for _ in xrange(self.resolution):
            delta_v = (0.04 * voltage * voltage) + (5*voltage) + 140 + current
            voltage += self.time_coefficient * delta_v
        self.set_voltage(voltage)

        return old_voltage == voltage and old_current == current

    def get_adjusted_voltage(self):
        return (min(self.get_voltage(), 30) - self.stable_voltage) / 100
