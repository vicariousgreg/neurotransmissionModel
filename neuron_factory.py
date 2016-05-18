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

from multiprocessing import Array, Queue, Process
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
        self.stable = True

    def initialize(self):
        self.neuron_environment.initialize()
        self.num_threads = min(self.num_threads, len(self.neurons))

        if self.num_threads == 1:
            self.multithreaded = False
            self.active = [True] * len(self.neurons)
        else:
            self.multithreaded = True
            # Create the boolean buffers
            self.active = Array('b', [True] * len(self.neurons), lock=False)
            length = int(ceil(float(len(self.neurons)) / self.num_threads))

            self.workers = []
            self.worker_in_queues = []
            self.worker_out_queues = []
            for i in xrange(self.num_threads):
                start_index,stop_index = (i * length, min(len(self.neurons), (i+1)*length))
                in_queue = Queue()
                out_queue = Queue()
                self.worker_in_queues.append(in_queue)
                self.worker_out_queues.append(out_queue)
                self.workers.append(Process(
                    target=self.work,
                    args=(start_index, stop_index, in_queue, out_queue)))

            for worker in self.workers: worker.start()

    def close(self):
        if self.multithreaded:
            for queue in self.worker_in_queues: queue.put(False)
     
    def step(self, count=1):
        # Hacky way of initializing without placing burden on caller.
        try: self.active
        except: self.initialize()

        for _ in xrange(count):
            tokens = set()

            # Activate drivers
            # Drivers do not step the neuron, but modify it to prepare for
            #     a timestep.  If True is returned, the neuron should be
            #     stepped during this timestep.
            for neuron,driver in self.neuron_drivers.iteritems():
                if driver.drive(neuron, self.time):
                    self.active[neuron.neuron_id] = True
                    self.stable = False

            # Tell workers to perform computation
            if self.multithreaded:
                if not self.stable:
                    for queue in self.worker_in_queues:
                        queue.put(True)
                    for queue in self.worker_out_queues:
                        tokens.update(queue.get())
            else:
                for i in xrange(len(self.neurons)):
                    if self.active[i]:
                       tokens.update( self.neurons[i].step())

            # Record neuron somas
            for neuron,probe in self.neuron_probes.iteritems():
                probe.record(neuron.soma)

            # Record components with probes
            for component,probe in self.concentration_probes.iteritems():
                probe.record(component)

            # Step the environment.
            if self.neuron_environment.step(): self.stable += 1
            self.time += 1
            
            if not self.stable:
                for i in xrange(len(self.active)): self.active[i] = False
            if len(tokens) > 0:
                self.stable = False
                for token in tokens: self.active[token] = True
            else:
                self.stable_count += 1
                self.stable = True

    def work(self, start_index, stop_index, in_queue, out_queue):
        while in_queue.get():
            #print("Worker", start_index)
            new_tokens = set()
            for neuron_id in xrange(start_index, stop_index):
                if self.active[neuron_id]:
                    #print(neuron_id)
                    new_tokens.update(self.neurons[neuron_id].step())
            #if len(new_tokens) > 0: print(new_tokens)
            out_queue.put(new_tokens)

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
