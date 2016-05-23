# Soma Model
#
# The parameter a describes the time scale of the recovery variable
# u. Smaller values result in slower recovery. A typical value is
# a = 0.02.
#
# The parameter b describes the sensitivity of the recovery variable
# u to the subthreshold fluctuations of the membrane potential v.
# Greater values couple v and u more strongly resulting in possible
# subthreshold oscillations and low-threshold spiking dynamics. A
# typical value is b = 0.2. The case b<a(b>a) corresponds
# to saddle-node (Andronov-Hopf) bifurcation of the resting state
# [10].
#
# The parameter c describes the after-spike reset value of the membrane
# potential v caused by the fast high-threshold K+ conductances.
# A typical value is c = -65 mV
#
# The parameter d describes after-spike reset of the recovery variable
# u caused by slow high-threshold Na+ and K+ conductances.
# A typical value is d = 2.

from enum import enum

# Parameter constants.
SOMA_TYPES = enum(
    DEFAULT          = (0.02, 0.2 , -70.0, 2   ), # Default
    REGULAR          = (0.02, 0.2 , -65.0, 8   ), # Regular Spiking
    BURSTING         = (0.02, 0.2 , -55.0, 4   ), # Intrinsically Bursting
    CHATTERING       = (0.02, 0.2 , -50.0, 2   ), # Chattering
    FAST             = (0.1 , 0.2 , -65.0, 2   ), # Fast Spiking
    LOW_THRESHOLD    = (0.02, 0.25, -65.0, 2   ), # Low Threshold
    THALAMO_CORTICAL = (0.02, 0.25, -65.0, 0.05), # Thalamo-cortical
    RESONATOR        = (0.1 , 0.26, -65.0, 2   ), # Resonator
    PHOTORECEPTOR    = (0   , 0   , -82.6, 0   ), # Photoreceptor
    HORIZONTAL       = (0   , 0   , -82.6, 0   )  # Horizontal Cell
)

class Soma:
    def __init__(self, soma_type=SOMA_TYPES.DEFAULT, environment=None, record=False, resolution=100):
        self.stable_count = 0
        self.environment = environment
        self.resolution = resolution
        self.time_coefficient = 1.0 / resolution
        self.record = record
        self.soma_type = soma_type
        self.reset()

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

    def reset(self):
        self.a, self.b, self.c, self.d = self.soma_type
        self.u = self.b * self.c
        self.prev_voltage = self.c

        # Only reset if already registered.
        # Otherwise, register.
        try:
            self.env_id
            self.set_voltage(self.c)
        except AttributeError:
            self.env_id = self.environment.register(self.c, record=self.record)

    def step(self, current=0.0):
        voltage = self.get_voltage()
        voltage = self.cycle(voltage, current)

        if abs(voltage-self.prev_voltage) < 0.001:
            self.stable_count += 1
        else:
            self.stable_count = 0
        self.prev_voltage = voltage

        return self.stable_count > 10

    def cycle(self, voltage, current):
        """
        Cycles the voltage and currents.
        Voltage is a parameter to avoid accessing the voltage cache.

        v' = 0:04vv + 5v + 140 - u + I
        u' = a(bv - u)
        with the auxiliary after-spike resetting
        if 30 mV; then v = c and u = u + d
        """
        if voltage > 30:
            voltage = self.c
            self.u = self.u + self.d

        for _ in xrange(self.resolution):
            if voltage > 30:
                #print("SPIKE")
                break
            else:
                delta_v = (0.04 * voltage * voltage) + (5*voltage) + 140 - self.u + current
                voltage += self.time_coefficient * delta_v
        self.u += self.a * ((self.b * voltage) - self.u)
        self.set_voltage(voltage)
        return voltage

    def get_adjusted_voltage(self):
        return (min(self.get_voltage(), 30) - self.c) / 100
