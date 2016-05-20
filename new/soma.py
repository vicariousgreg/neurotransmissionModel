# Soma Model

class Soma:
    def __init__(self, environment=None, resolution=100):
        self.stable_count = 0
        self.environment = environment
        self.stable_voltage = -70
        self.env_id = environment.register(self.stable_voltage)
        self.resolution = resolution
        self.time_coefficient = 1.0 / resolution
        self.reset(reset_voltage=False)

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

    def reset(self, reset_voltage=True):
        self.u = -14.0

        # Only reset if indicated
        # This can break the environment if other neurons aren't yet registered
        if reset_voltage: self.set_voltage(self.stable_voltage)

        # The parameter a describes the time scale of the recovery variable
        # u. Smaller values result in slower recovery. A typical value is
        # a = 0.02.
        self.a = 0.02

        # The parameter b describes the sensitivity of the recovery variable
        # u to the subthreshold fluctuations of the membrane potential v.
        # Greater values couple v and u more strongly resulting in possible
        # subthreshold oscillations and low-threshold spiking dynamics. A
        # typical value is b = 0.2. The case b<a(b>a) corresponds
        # to saddle-node (Andronov-Hopf) bifurcation of the resting state
        # [10].
        self.b = 0.2

        # The parameter c describes the after-spike reset value of the membrane
        # potential v caused by the fast high-threshold K+ conductances.
        # A typical value is c = -65 mV
        self.c = -70.0

        # The parameter d describes after-spike reset of the recovery variable
        # u caused by slow high-threshold Na+ and K+ conductances.
        # A typical value is d = 2.
        self.d = 2

    def step(self, current=0.0):
        voltage = self.get_voltage()
        self.cycle(voltage, current)

        if ligand_activation == 0.0 and \
                abs(voltage-self.stable_voltage) < 0.001:
            self.stable_count += 1
        else:
            self.stable_count = 0

        return self.stable_count > 10 and self.current == 0.0

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
                print("SPIKE")
                break
            else:
                delta_v = (0.04 * voltage * voltage) + (5*voltage) + 140 - self.u + current
                voltage += time_coefficient * delta_v
        self.u += self.a * ((self.b * voltage) - self.u)
        self.set_voltage(voltage)

    def get_adjusted_voltage(self):
        return (min(self.get_voltage(), 30) - self.stable_voltage) / 100
