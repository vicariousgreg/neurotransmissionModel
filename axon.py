# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synaptic cleft.

from math import exp
from collections import deque

from molecule import Transporters
from environment import betav

class Axon:
    def __init__(self, transporter=Transporters.GLUTAMATE, reuptake_rate=0.5,
                    capacity=1.0, replenish_rate=0.1, delay=None, verbose=False):
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
        self.protein = transporter
        self.native_mol_id = transporter.native_mol_id
        self.capacity = capacity
        self.density = reuptake_rate
        self.affinities = transporter.affinities
        self.concentration = capacity

        self.replenish_rate = replenish_rate
        baseline_voltage = -65.0

        self.delay = delay
        if delay:
            self.voltage_queue = deque()
            for _ in xrange(delay):
                self.voltage_queue.appendleft(baseline_voltage)
        else:
            self.voltage_queue = None
            self.voltage = baseline_voltage

        self.verbose = verbose
        self.releasing = False
        self.voltage_threshold=-64.0

    def get_concentration(self, mol_id=None):
        return self.concentration

    def set_concentration(self, new_concentration, mol_id=None):
        self.concentration = new_concentration

    def add_concentration(self, delta, mol_id=None):
        self.concentration += delta

    def remove_concentration(self, delta, mol_id=None):
        self.concentration -= delta

    def step(self, voltage=None):
        """
        Cycles the axon with an optional input |voltage| from the soma.
        Returns whether the axon is stable (not releasing). This is used by the
            neuron to determine if the synapse should be activated.
        """
        # If there is a delay, use the queue.
        if self.delay is not None:
            # Add voltage to queue
            self.voltage_queue.appendleft(voltage)
            # Remove voltage from queue
            voltage = self.voltage_queue.pop()

        if voltage:
            self.voltage = voltage
        else: self.voltage = self.voltage_threshold
        if self.voltage > self.voltage_threshold and not self.releasing:
            self.releasing = True
        return self.replenish() and not self.releasing

    def release(self):
        # Determine how many molecules to actually release.

        ### Non-stochastic release (faster)
        released = max(0.0, (self.voltage - self.voltage_threshold) / 500)
        ###

        ### Use beta distribution to release stochastically
        ### Rate 10 ensures low decrement.
        #difference = (self.voltage - self.voltage_threshold) / 500
        #released = max(0, min(self.get_concentration(),
        #    betav(difference, rate=10)))
        ###

        if released == 0.0:
            self.releasing = False
            return 0.0

        # Remove concentration.
        self.remove_concentration(released)
        if self.verbose: print("Released %f molecules" % released)

        return released

    def replenish(self):
        """
        Replenishes neurotransmitters if the axon is not at capacity.
        Returns whether the axon is at capacity.
        """
        missing = self.capacity - self.get_concentration()
        if missing <= 0 or self.replenish_rate == 0.0: return True
        elif missing < 0.00001:
            self.set_concentration(self.capacity)

        # Determine concentration to replenish

        ### Non-stochastic (faster)
        sample = self.replenish_rate * missing
        ###

        ### Use beta distribution to replenish stochastically
        #sample = betav(missing, rate=self.replenish_rate)
        ###

        self.add_concentration(sample)

        if self.verbose:
            print("Regenerated %f" % sample)
            print("Axon: %f" % self.get_concentration())

        return False

    def get_scaled_voltage(self):
        return min(0.2, (self.voltage-self.voltage_threshold)/100)
