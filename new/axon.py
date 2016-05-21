# Axon Model
#
# Models the axon of a presynaptic neurons, which pumps and reuptakes
#     neurotransmitters into and out of the synaptic cleft.

from collections import deque

from molecule import Transporters

class Axon:
    def __init__(self, synaptic_cleft, transporter=Transporters.GLUTAMATE,
                        reuptake_rate=0.5, capacity=1.0, replenish_rate=0.1,
                        delay=0, voltage_minimum=-70.0, voltage_maximum=30.0,
                        verbose=False):
        """
        Axons keep track of activation and release neurotransmitters over
            time.  Neurotransmitters are regenerated via reuptake and
            replenishing.

        |synaptic_cleft| is the synaptic cleft this axon releases into.
        |transporter| is the type of transporter on the axon membrane.
        |reuptake_rate| is the concentration of reuptake receptors on the
            membrane, and controls the rate of neurotransmitter reuptake.
        |capacity| is the neurotransmitter capacity in the axon vesicles.
        |replenish_rate| controls the regeneration of neurotransmitter 
            over time.  Higher values increase rate of restoration.
        |delay| specifies how long it takes the axon to respond, and sets
            the size of a queue.

        Axons respond directly to the voltage of the neuron, and have both a
            threshold minimum voltage for activity, and a ceiling for voltage.
        Voltage determines the rate of neurochemical release according to a
            particular release function.
        Release pulls from a pool tracked by self.concentration.  This pool is
            also automatically regenerated according to the |replenish rate|,
            and externally via reuptake from the synaptic cleft according to
            the |reuptake rate|.  This interaction is mediated by the synaptic
            cleft itself, and depends on the |transporter| protein on the axon.
        """
        self.synaptic_cleft = synaptic_cleft
        self.protein = transporter
        self.native_mol_id = transporter.native_mol_id
        self.capacity = capacity
        self.density = reuptake_rate
        self.affinities = transporter.affinities
        self.concentration = capacity

        self.replenish_rate = replenish_rate

        self.voltage_minimum = voltage_minimum
        self.voltage_maximum = voltage_maximum
        self.voltage = self.voltage_minimum

        self.delay = delay
        if delay:
            self.delay_queue = deque()
            for _ in xrange(delay):
                self.delay_queue.appendleft(self.voltage_minimum)
        else:
            self.delay_queue = None

        self.verbose = verbose

    def get_concentration(self):
        return self.concentration

    def set_concentration(self, new_concentration):
        self.concentration = new_concentration

    def add_concentration(self, delta):
        self.concentration += delta

    def remove_concentration(self, delta):
        self.concentration -= delta

    def step(self, voltage):
        """
        Cycles the axon.
        """
        # If there is a delay, use the queue.
        if self.delay > 0:
            # Add voltage to queue.  Bound between min and max.
            self.delay_queue.appendleft(
                max(self.voltage_minimum,
                    min(voltage, self.voltage_maximum)))
            # Remove voltage from queue.
            self.voltage = self.delay_queue.pop()
        else: self.voltage = voltage

        stable = self.replenish()
        stable &= self.release()
        return self.synaptic_cleft.step() & stable

    def release(self):
        """
        Releases neurochemical into the synaptic cleft.
        Returns whether the axon is stable (no release).
        """
        # Determine how many molecules to actually release.
        if self.voltage > self.voltage_minimum:
            released = 1.0
            #released = min(self.concentration) #, f(self.voltage)) ### CHANGE ME

            # Remove concentration.
            self.remove_concentration(released)
            if self.verbose: print("Released %f molecules" % released)
            print("Released %f molecules" % released)
            self.synaptic_cleft.add_concentration(released, self.native_mol_id)
            return False
        else: return True

    def replenish(self):
        """
        Replenishes neurotransmitters if the axon is not at capacity.
        Returns whether the axon is stable (at capacity).
        """
        missing = self.capacity - self.get_concentration()
        if missing <= 0 or self.replenish_rate == 0.0: return True
        elif missing < 0.00001:
            self.set_concentration(self.capacity)

        # Determine concentration to replenish
        sample = self.replenish_rate * missing

        self.add_concentration(sample)

        if self.verbose:
            print("Regenerated %f" % sample)
            print("Axon: %f" % self.get_concentration())

        return False

    def get_adjusted_voltage(self):
        return min((self.voltage-self.voltage_minimum)/100)
