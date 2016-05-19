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

class PhotoreceptorSoma:
    def __init__(self, environment=None):
        self.stable_count=0
        self.base_conductance = 0.8
        self.light_level = 0.0

        self.environment = environment
        self.stable_voltage = -40.1323467956
        self.neuron_id = environment.register(self.stable_voltage)
        self.stable_count = 0
        self.reset(reset_voltage=False)

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

    def adjust_voltage(self, delta):
        """
        NEEDS TO BE THREAD SAFE
        """
        self.environment.adjust_voltage(self.neuron_id, delta)

    def reset(self, reset_voltage=True):
        self.prev_voltage = self.stable_voltage
        if reset_voltage: self.set_voltage(-65.0)
        self.h=0.0511587915373
        self.n=0.677131688462
        self.m=self.base_conductance
        self.iapp = 0.0

        self.cm=1.0
        self.gnabar=120.0
        self.gkbar=36.0
        self.gl=0.3
        self.vna=50.0
        self.vk=-77.0
        self.vl=-54.4

    def step(self, light_activation=0.0, resolution=100, silent=False):
        time_coefficient = 1.0 / resolution

        voltage = self.get_voltage()
        self.light_level += (light_activation - self.light_level) / 1000
        self.m = self.base_conductance - self.light_level
        self.cycle(time_coefficient, voltage)

        if silent: return

        if voltage == self.prev_voltage:
            self.stable_count += 1
        else:
            self.stable_count = 0
        self.prev_voltage = voltage
        return self.stable_count > 10 and self.iapp == 0.0

    def cycle(self, time_coefficient, voltage):
        ah   = 0.07*exp(-(voltage+65.0)/20.0)
        bh   = 1.0/( 1.0 + exp(-(voltage+35.0)/10.0) )
        hinf = ah/(ah+bh)
        tauh = 1/(ah+bh)

        an   = 0.01*(voltage + 55.0)/(1.0 - exp(-(voltage + 55.0)/10.0))
        bn   = 0.125*exp(-(voltage + 65.0)/80.0)
        ninf = an/(an+bn)
        taun = 1.0/(an+bn)

        ina = self.gnabar * (self.m**3) * self.h * (voltage-self.vna)
        ik  = self.gkbar * (self.n**4) * (voltage-self.vk)
        il  = self.gl * (voltage-self.vl)

        self.adjust_voltage(time_coefficient*(-ina - ik - il ) / self.cm)
        self.h +=  time_coefficient*(hinf - self.h)/tauh
        self.n +=  time_coefficient*(ninf - self.n)/taun

    def get_scaled_voltage(self):
        return (self.get_voltage()-self.stable_voltage)/100
