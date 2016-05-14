# Photoreceptor Model
#
# Photoreceptors do not generate action potentials.  Instead, they have a base
#     current that triggers the release of glutamate in the dark.  With light
#     activation, ion conductance is reduced, and less glutamate is released.
#     The end result is high release in the dark, low release in the light.
#
# Adapted from Hodgkin-Huxley model implementation by G. Bard Ermentrout
# http://www.math.pitt.edu/~bard/bardware/hh-c.ode

from math import exp

class Photoreceptor:
    def __init__(self):
        self.data = []
        self.stabilization_counter=0
        self.base_conductance = 0.8
        self.light_level = 0.0
        self.reset()

    def reset(self):

        self.v=-65.0
        self.h=0.596
        self.n=0.318
        self.m=self.base_conductance

        self.cm=1.0
        self.gnabar=120.0
        self.gkbar=36.0
        self.gl=0.3
        self.vna=50.0
        self.vk=-77.0
        self.vl=-54.4

        # Stabilize
        for _ in xrange(20000): self.step(silent=True)
        self.stable_voltage = self.v

    def step(self, light_activation=0.0, resolution=100, silent=False):
        if light_activation == 0.0 and self.stabilization_counter > 1:
            if not silent: self.data.append((self.v-self.stable_voltage)/100)
            return
        time_coefficient = 1.0 / resolution

        self.light_level += (light_activation - self.light_level) / 1000
        self.m = self.base_conductance - self.light_level
        self.cycle(time_coefficient)

        if silent: return

        self.data.append((self.v-self.stable_voltage)/100)

        if self.v == self.stable_voltage:
            self.stabilization_counter += 1
        else:
            self.stabilization_counter = 0


    def cycle(self, time_coefficient):
        ah   = 0.07*exp(-(self.v+65.0)/20.0)
        bh   = 1.0/( 1.0 + exp(-(self.v+35.0)/10.0) )
        hinf = ah/(ah+bh)
        tauh = 1/(ah+bh)

        an   = 0.01*(self.v + 55.0)/(1.0 - exp(-(self.v + 55.0)/10.0))
        bn   = 0.125*exp(-(self.v + 65.0)/80.0)
        ninf = an/(an+bn)
        taun = 1.0/(an+bn)

        ina = self.gnabar * (self.m**3) * self.h * (self.v-self.vna)
        ik  = self.gkbar * (self.n**4) * (self.v-self.vk)
        il  = self.gl * (self.v-self.vl)

        self.v +=  time_coefficient*(-ina - ik - il ) / self.cm
        self.h +=  time_coefficient*(hinf - self.h)/tauh
        self.n +=  time_coefficient*(ninf - self.n)/taun

    def get_data(self, name = "photoreceptor voltage"):
        return (name, self.data)
