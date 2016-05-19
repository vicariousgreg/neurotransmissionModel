# Photoreceptor Soma Model
#
# Photoreceptors do not generate action potentials.  Instead, they have a base
#     current that triggers the release of glutamate in the dark.  With light
#     activation, ion conductance is reduced, and less glutamate is released.
#     The end result is high release in the dark, low release in the light.

class PhotoreceptorSoma:
    def __init__(self, environment=None):
        self.current = 0
        self.environment = environment
        self.stable_voltage = -82.6556443707
        self.neuron_id = environment.register(self.stable_voltage)

        self.firing = False
        self.light_level = 0.0
        self.gap_current = 0.0

    def get_voltage(self):
        """
        NEEDS TO BE THREAD SAFE
        """
        return self.environment.get_voltage(self.neuron_id)

    def set_voltage(self, v):
        """
        NEEDS TO BE THREAD SAFE
        """
        self.environment.set_voltage(self.neuron_id, v)

    def step(self, light_activation=0.0, resolution=100):
        self.light_level += (light_activation - self.light_level) / 10
        current = self.gap_current + self.current - self.light_level
        time_coefficient = 1.0 / resolution

        voltage = self.get_voltage()
        for _ in xrange(resolution):
            delta_v = (0.04 * voltage * voltage) + (5*voltage) + 140 + current
            voltage += time_coefficient * delta_v
        self.set_voltage(voltage)

        return False

    def get_scaled_voltage(self):
        return (min(self.get_voltage(), 30) - self.stable_voltage) / 100
