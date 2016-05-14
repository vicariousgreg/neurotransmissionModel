# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synaptic cleft.

from math import exp
from collections import deque

from molecule import Transporters
from membrane import TransporterMembrane

class Axon(TransporterMembrane):
    def __init__(self, transporter=Transporters.GLUTAMATE, reuptake_rate=0.5,
                    capacity=1.0, replenish_rate=0.1, delay=None,
                    environment=False, verbose=False):
        """
        Axons keep track of activation and release neurotransmitters over
            time.  Neurotransmitters are regenerated via reuptake and
            replenishing.

        |transporter| is the type of transporter on the axon membrane.
        |reuptake_rate| is the concentration of reuptake receptors on the
            membrane, and controls the rate of neurotransmitter reuptake.
        |capacity| is the neurotransmitter capacity in the axon vesicles.
        |replenish_rate| controls the regeneration of neurotransmitter 
            over time.  Higher values increase rate of restoration.
        """
        # Initialize as pool cluster
        TransporterMembrane.__init__(self, transporter, reuptake_rate, capacity, environment)

        self.replenish_rate = replenish_rate

        if delay:
            self.voltage_queue = deque()
            for _ in xrange(delay): self.voltage_queue.appendleft(None)
        else: self.voltage_queue = None

        self.verbose = verbose

        self.stabilization_counter = 0
        self.reset()


    def reset(self):
        self.time = 0

        self.v=-65.0
        self.n=0.318

        self.cm=1.0
        self.gcabar=36.0
        self.gl=0.3
        self.vca=-65
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

    def step(self, voltage=None, resolution=100, silent=False):
        time_coefficient = 1.0 / resolution

        # If there is a delay, use the queue.
        if self.voltage_queue:
            # Add voltage to queue
            self.voltage_queue.appendleft(voltage)
            # Remove voltage from queue
            voltage = self.voltage_queue.pop()

        if voltage: self.v = voltage
        self.cycle(time_coefficient)

        if silent: return
        self.time += 1

    def cycle(self, time_coefficient):
        an   = 0.01*(self.v + 55.0)/(1.0 - exp(-(self.v + 55.0)/10.0))
        bn   = 0.125*exp(-(self.v + 65.0)/80.0)
        ninf = an/(an+bn)
        taun = 1.0/(an+bn)

        self.ica  = self.gcabar * (self.n**4) * (self.v-self.vca)
        il  = self.gl * (self.v-self.vl)

        self.v +=  time_coefficient*(-self.ica - il ) / self.cm
        self.n +=  time_coefficient*(ninf - self.n)/taun

    def release(self):
        # Determine how many molecules to actually release.

        ### Non-stochastic release (faster)
        released = max(0.0, (self.v - self.stable_voltage) / 500)
        ###

        ### Use beta distribution to release stochastically
        ### Rate 10 ensures low decrement.
        #difference = (self.v - self.stable_voltage) / 500
        #released = max(0, min(self.get_native_concentration(),
        #    self.environment.beta(difference, rate=10)))
        ###

        if released == 0.0:
            return 0.0

        # Remove concentration.
        self.remove_concentration(released, self.native_mol_id)
        if self.verbose: print("Released %f molecules" % released)

        return released

    def replenish(self):
        """
        Replenishes neurotransmitters if the axon is not at capacity.
        """
        missing = self.capacity - self.get_native_concentration()
        if missing <= 0 or self.replenish_rate == 0.0: return
        elif missing < 0.00001:
            self.set_concentration(self.capacity, self.native_mol_id)

        # Determine concentration to replenish

        ### Non-stochastic (faster)
        sample = self.replenish_rate * missing
        ###

        ### Use beta distribution to replenish stochastically
        #sample = self.environment.beta(missing, rate=self.replenish_rate)
        ###

        self.add_concentration(sample, self.native_mol_id)

        if self.verbose:
            print("Regenerated %f" % sample)
            print("Axon: %f" % self.get_concentration(self.native_mol_id))

    def get_scaled_voltage(self):
        return min(0.2, (self.get_voltage()-self.stable_voltage)/100)
