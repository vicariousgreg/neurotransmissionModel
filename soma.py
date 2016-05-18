# Soma Model
#
# Adapted from Hodgkin-Huxley model implementation by G. Bard Ermentrout
# http://www.math.pitt.edu/~bard/bardware/hh-c.ode

from math import exp

class Soma:
    def __init__(self, base_current=0.0, environment=None):
        self.iapp = base_current
        self.stable_count = 0
        self.environment = environment
        self.stable_voltage = -64.9997224337
        self.neuron_id = environment.register(self.stable_voltage)
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
        self.environment.adjust_voltage(self.neuron_id, delta)

    def reset(self, reset_voltage=True):
        self.firing = False
        self.gap_current = 0.0

        # Only reset if indicated
        # This can break the environment if other neurons aren't yet registered
        if reset_voltage: self.set_voltage(self.stable_voltage)
        self.h=0.596111046355
        self.n=0.31768116758
        self.m=0.0529342176209

        self.cm=1.0
        self.gnabar=120.0
        self.gkbar=36.0
        self.gl=0.3
        self.vna=50.0
        self.vk=-77.0
        self.vl=-54.4


        # Stabilize
        '''
        old_v = 0
        stable = 0
        while stable < 10:
            self.environment.step()
            new_v = self.get_voltage()
            print(new_v)
            if old_v == new_v:
                stable += 1
            else:
                stable = 0
                old_v = new_v
            self.step(silent=True)
        self.environment.step()
        '''

    def step(self, ligand_activation=0.0, resolution=100, silent=False):
        voltage = self.get_voltage()
        time_coefficient = 1.0 / resolution
        self.m += ligand_activation
        voltage_delta = self.cycle(time_coefficient, voltage)
        if silent: return

        if voltage > 0.0 and self.firing is False:
            print("SPIKE")
            self.firing = True
        elif self.firing and voltage < 0.0:
            self.firing = False

        if ligand_activation == 0.0 and \
                abs(voltage-self.stable_voltage) < 0.001:
            self.stable_count += 1
        else:
            self.stable_count = 0

        return self.stable_count > 10 and self.iapp == 0.0

    def cycle(self, time_coefficient, voltage):
        """
        Cycles the voltage and currents.
        Voltage is a parameter to avoid accessing the voltage cache.
        """
        am   = 0.1*(voltage+40.0)/( 1.0 - exp(-(voltage+40.0)/10.0) )
        bm   = 4.0*exp(-(voltage+65.0)/18.0)
        minf = am/(am+bm)
        taum = 1.0/(am+bm)

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

        self.adjust_voltage(time_coefficient*( self.gap_current + self.iapp - ina - ik - il ) / self.cm)
        self.h +=  time_coefficient*(hinf - self.h)/tauh
        self.n +=  time_coefficient*(ninf - self.n)/taun
        self.m +=  time_coefficient*(minf - self.m)/taum

    def get_scaled_voltage(self):
        return min(0.2, (self.get_voltage()-self.stable_voltage)/100)
