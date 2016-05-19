# Photoreceptor Soma Model
#
# Photoreceptors do not generate action potentials.  Instead, they have a base
#     current that triggers the release of glutamate in the dark.  With light
#     activation, ion conductance is reduced, and less glutamate is released.
#     The end result is high release in the dark, low release in the light.
#
# Adapted from Hodgkin-Huxley model implementation by G. Bard Ermentrout
# http://www.math.pitt.edu/~bard/bardware/hh-c.ode

from math import exp
from soma import Soma

class PhotoreceptorSoma(Soma):
    def __init__(self, environment=None):
        Soma.__init__(self, base_current=2, environment=environment)
        self.stable_count=0
        self.light_level = 0.0
        self.stable_voltage = -40.1323467956

        self.environment = environment
        self.neuron_id = environment.register(self.stable_voltage)
        self.stable_count = 0
       # self.reset(reset_voltage=False)

    def step(self, light_activation=0.0, resolution=100):
        voltage = self.get_voltage()
        self.light_level = light_activation
        #self.light_level += (light_activation - self.light_level) / 10
        self.cycle(resolution, voltage, self.gap_current + self.current - self.light_level)
        print(self.gap_current + self.current - self.light_level)
        #raw_input()
        self.firing = False

        if light_activation == 0.0 and \
                abs(voltage-self.stable_voltage) < 0.001:
            self.stable_count += 1
        else:
            self.stable_count = 0
        self.stable_count = 0

        return self.stable_count > 10 and self.current == 0.0


    def get_scaled_voltage(self):
        return self.get_voltage()
