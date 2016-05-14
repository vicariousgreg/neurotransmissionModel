# Soma Model
#
# Adapted from Hodgkin-Huxley model implementation by G. Bard Ermentrout
# http://www.math.pitt.edu/~bard/bardware/hh-c.ode

from math import exp

class Soma:
    def __init__(self, base_current=0.0):
        self.data = []
        self.iapp = base_current
        self.stabilization_counter=0
        self.reset()

    def reset(self):
        self.time = 0
        self.firing = False
        self.last_spike = 0
        self.gap_current = 0.0

        self.v=-65.0
        self.h=0.596
        self.n=0.318
        self.m=0.053

        self.cm=1.0
        self.gnabar=120.0
        self.gkbar=36.0
        self.gl=0.3
        self.vna=50.0
        self.vk=-77.0
        self.vl=-54.4

        # Stabilize
        old_v = 0
        stable = 0
        while stable < 1000:
            if old_v == self.v:
                stable += 1
            else:
                stable = 0
                old_v = self.v
            self.step(0.0, silent=True)
        self.stable_voltage = self.v

    def step(self, ligand_activation, resolution=100, silent=False):
        if ligand_activation == 0 and self.iapp == 0.0 \
                and self.stabilization_counter > 1:
            self.data.append(min(0.2, (self.v-self.stable_voltage)/100))
            return
        time_coefficient = 1.0 / resolution
        self.m += ligand_activation
        self.cycle(time_coefficient)
        if silent: return

        self.data.append(min(0.2, (self.v-self.stable_voltage)/100))

        if self.v > 0.0 and self.firing is False:
            time = len(self.data)
            print(time - self.last_spike)
            self.last_spike = time
            self.firing = True
        elif self.firing and self.v < 0.0:
            self.firing = False
        self.time += 1

        if self.v == self.stable_voltage:
            self.stabilization_counter += 1
        else:
            self.stabilization_counter = 0


    def cycle(self, time_coefficient):
        am   = 0.1*(self.v+40.0)/( 1.0 - exp(-(self.v+40.0)/10.0) )
        bm   = 4.0*exp(-(self.v+65.0)/18.0)
        minf = am/(am+bm)
        taum = 1.0/(am+bm)

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

        self.v +=  time_coefficient*( self.gap_current - self.iapp - ina - ik - il ) / self.cm
        self.h +=  time_coefficient*(hinf - self.h)/tauh
        self.n +=  time_coefficient*(ninf - self.n)/taun
        self.m +=  time_coefficient*(minf - self.m)/taum

    def get_data(self, name = "soma voltage"):
        return (name, self.data)
