# Neuron Factory
#
# The Neuron Factory is used to create and manage neurons and synapses.  It
#     holds the neuron environment and can easily simulate a timestep on all
#     components it holds.
#
# Drivers can be added to activate particular neurons at each timestep.
# 
# Probes can be added to any component to take measurements of voltage, current,
#     or concentration over the course of the simulation.

from multiprocessing import Array, Process
from math import ceil
from environment import NeuronEnvironment
from neuron import Neuron, NeuronTypes
from molecule import Transporters, Receptors, Molecule_IDs

class NeuronFactory:
    def __init__(self, num_threads=1):
        self.neuron_environment = NeuronEnvironment()
        self.neurons = []
        self.synapses = []

        self.drivers = {}
        self.neuron_drivers = {}
        self.probes = {}
        self.neuron_probes = {}
        self.concentration_probes = {}

        self.num_threads = num_threads
        self.time = 0
        self.stable_count = 0
        self.stable = False

    def initialize(self):
        self.neuron_environment.initialize()
        self.num_threads = min(self.num_threads, len(self.neurons))

        if self.num_threads == 1:
            self.multithreaded = False
            self.prev_active = [False] * len(self.neurons)
            self.next_active = [False] * len(self.neurons)
        else:
            self.multithreaded = True
            # Create the boolean buffers
            self.prev_active = Array('b', [False] * len(self.neurons), lock=False)
            self.next_active = Array('b', [False] * len(self.neurons), lock=False)
            length = int(ceil(float(len(self.neurons)) / self.num_threads))

            # Create workers
            self.workers = []
            for i in xrange(self.num_threads):
                start_index,stop_index = (i * length, min(len(self.neurons), (i+1)*length))
                self.workers.append(Process(
                    target=self.work,
                    args=(start_index, stop_index)))

        # Activate drivers
        # Drivers do not step the neuron, but modify it to prepare for
        #     a timestep.  If True is returned, the neuron should be
        #     stepped during this timestep.
        for neuron,driver in self.neuron_drivers.iteritems():
            if driver.drive(neuron, self.time):
                self.prev_active[neuron.neuron_id] = True
                self.stable = False

        if self.multithreaded:
            for worker in self.workers: worker.start()

    def close(self):
        if self.multithreaded:
            for worker in self.workers: worker.terminate()
     
    def step(self, count=1):
        # Hacky way of initializing without placing burden on caller.
        try: self.prev_active
        except: self.initialize()

        for _ in xrange(count):
            # If no other threads, do it yourself
            if not self.multithreaded:
                tokens = set()
                for i in xrange(len(self.neurons)):
                    if self.prev_active[i]:
                       tokens.update( self.neurons[i].step())
                       self.prev_active[i] = False
                for token in tokens:
                    self.next_active[token] = True

            # Record neuron somas
            for neuron,probe in self.neuron_probes.iteritems():
                probe.record(neuron.soma)

            # Record components with probes
            for component,probe in self.concentration_probes.iteritems():
                probe.record(component)

            # Step the environment.
            self.neuron_environment.step()
            self.time += 1
            if self.time % 100 == 0: print(self.time)
            
            # Wait for workers to finish up tasks
            # If single threaded, this loop won't run
            while any(x == True for x in self.prev_active): pass

            # If there are no threads to run next, we are stable for now
            if not any(x for x in self.next_active):
                self.stable_count += 1
                self.stable = True
                print("**********************")

            # Activate drivers
            # Drivers do not step the neuron, but modify it to prepare for
            #     a timestep.  If True is returned, the neuron should be
            #     stepped during this timestep.
            for neuron,driver in self.neuron_drivers.iteritems():
                if driver.drive(neuron, self.time):
                    self.next_active[neuron.neuron_id] = True

            # Move buffers
            for i in xrange(len(self.next_active)):
                self.prev_active[i] = self.next_active[i]
                self.next_active[i] = False

    def work(self, start_index, stop_index):
        while True:
            for neuron_id in xrange(start_index, stop_index):
                if self.prev_active[neuron_id]:
                    for i in self.neurons[neuron_id].step():
                        self.next_active[i] = True
                    self.prev_active[neuron_id] = False

    def create_neuron(self, base_current=0.0,
            neuron_type=NeuronTypes.GANGLION, probe_name=None):
        neuron = Neuron(
            neuron_id=len(self.neurons),
            base_current=base_current,
            neuron_type=neuron_type,
            environment=self.neuron_environment)
        self.neurons.append(neuron)
        if probe_name:
            probe = VoltageProbe()
            self.probes[probe_name] = probe
            self.neuron_probes[neuron] = probe
        return neuron

    def create_neuron_grid(self, width, height,
            base_current=0.0, neuron_type=NeuronTypes.PHOTORECEPTOR):
        output = []
        for i in xrange(height):
            row = []
            for j in xrange(width):
                row.append(self.create_neuron(base_current, neuron_type))
            output.append(row)
        return output

    def create_synapse(self, pre_neuron, post_neuron,
            transporter=Transporters.GLUTAMATE, receptor=Receptors.AMPA,
            enzyme_concentration=1.0,
            axon_delay=None, dendrite_strength=0.05, active_molecules=[Molecule_IDs.GLUTAMATE],
            axon_probe_name=None, cleft_probe_name=None, dendrite_probe_name=None):
        # If single molecule is true, the synapse will save time and space by
        #     assuming that only one molecule will move through it.  This means
        #     that the proteins must use the same native molecule, and no
        #     exogenous molecules can be admitted into the synapse.
        # First, we must validate that the proteins use the same molecule.
        # Then we ensure that the molecule is in active_molecules.
        if transporter.native_mol_id != receptor.native_mol_id:
            raise ValueError
        if transporter.native_mol_id not in active_molecules:
            active_molecules.append(transporter.native_mol_id)

        # Create synapse.
        synapse = Neuron.create_synapse(pre_neuron, post_neuron,
            transporter=transporter, receptor=receptor,
            active_molecules = active_molecules, enzyme_concentration=enzyme_concentration,
            axon_delay=axon_delay, dendrite_strength=dendrite_strength)
        self.synapses.append(synapse)

        # Set up probes.
        if axon_probe_name:
            axon = synapse.axon
            probe = ConcentrationProbe(axon.native_mol_id)
            self.concentration_probes[axon] = probe
            self.probes[axon_probe_name] = probe
        if cleft_probe_name:
            cleft = synapse.synaptic_cleft
            probe = ConcentrationProbe(synapse.axon.native_mol_id)
            self.concentration_probes[cleft] = probe
            self.probes[cleft_probe_name] = probe
        if dendrite_probe_name:
            dendrite = synapse.dendrites[0]
            probe = ConcentrationProbe(dendrite.native_mol_id)
            self.concentration_probes[dendrite] = probe
            self.probes[dendrite_probe_name] = probe
        return synapse

    def create_gap_junction(self, pre_neuron, post_neuron, conductance=1.0):
        Neuron.create_gap_junction(pre_neuron, post_neuron, conductance)

    def register_driver(self, neuron, driver, name=None):
        self.neuron_drivers[neuron] = driver
        self.drivers[name] = driver

    def get_probe_data(self, name):
        return (name, self.probes[name].data)

    def get_driver_data(self, name):
        return (name, self.drivers[name].data)

class ConstantDriver:
    def __init__(self, activation=0.0, delay=0):
        self.activation = activation
        self.delay = delay
        if delay > 0: self.drive = self.predelay
        else: self.drive = self.postdelay

    def predelay(self, neuron, time):
        if time-self.delay >= 0:
            self.drive = self.postdelay
            neuron.external_activate(self.activation)
            return True
        else: return False

    def postdelay(self, neuron, time):
        neuron.external_activate(self.activation)
        return True

class CurrentPulseDriver:
    def __init__(self, current=0.0, period=1000, length=500,
                        delay=0, record=False):
        self.current = current
        self.period = period
        self.length = length
        self.delay = delay
        self.record = record
        self.data = []
        self.on = False

    def drive(self, neuron, time):
        time -= self.delay
        if time >= 0 and time % self.period == 0:
            self.on = True
            neuron.apply_current(self.current)
        elif time % self.period == self.length:
            self.on = False
            neuron.apply_current(0.0)
            return True
        if self.record: self.data.append(-0.2 if self.on else -0.3)
        if self.on: return True
        else: return False

class ActivationPulseDriver:
    def __init__(self, activation=0.0, period=1000, length=1,
                    delay=0, decrement=None, record=False):
        self.activation = activation
        self.period = period
        self.length = length
        self.delay = delay
        self.decrement = decrement
        self.record = record
        self.data = []

    def drive(self, neuron, time):
        time -= self.delay
        if time >= 0 and time % self.period < self.length:
            if self.record: self.data.append(-0.3)
            if self.decrement:
                self.activation = max(0.0, self.activation - self.decrement)
            if self.activation != 0.0:
                neuron.external_activate(self.activation)
                return True
            else: return False
        else:
            if self.record: self.data.append(-0.4)
            return False

class VoltageProbe:
    def __init__(self):
        self.data = []

    def record(self, component):
        self.data.append(component.get_scaled_voltage())

class ConcentrationProbe:
    def __init__(self, mol_id):
        self.data = []
        self.mol_id = mol_id

    def record(self, component):
        self.data.append(component.get_concentration(self.mol_id))
