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
from environment import Environment
from neuron import Neuron, NeuronTypes
from molecule import Transporters, Receptors, Molecule_IDs

class NeuronFactory:
    def __init__(self, num_threads=1):
        self.environment = Environment()
        self.neurons = []
        self.synapses = []

        self.drivers = {}
        self.neuron_drivers = {}
        self.concentration_probes = {}

        self.num_threads = num_threads
        self.time = 0

    def initialize(self):
        self.environment.initialize()
        self.num_threads = min(self.num_threads, len(self.neurons))

        if self.num_threads == 1:
            self.multithreaded = False
            self.active = [True] * len(self.neurons)
        else:
            self.multithreaded = True
            # Create the boolean buffers
            self.active = Array('b', [True] * len(self.neurons), lock=False)
            length = int(ceil(float(len(self.neurons)) / self.num_threads))

            # Create workers
            self.workers = []
            for i in xrange(self.num_threads):
                start_index,stop_index = (i * length, min(len(self.neurons), (i+1)*length))
                self.workers.append(Process(
                    target=self.work,
                    args=(start_index, stop_index)))

        # Activate drivers
        self.drive()

        # Start worker threads
        if self.multithreaded:
            for worker in self.workers: worker.start()

    def close(self):
        if self.multithreaded:
            for worker in self.workers: worker.terminate()

    def drive(self):
        # Activate drivers
        # Drivers do not step the neuron, but modify it to prepare for
        #     a timestep.  If True is returned, the neuron should be
        #     stepped during this timestep.
        for neuron,driver in self.neuron_drivers.iteritems():
            driver.drive(neuron, self.time)

    def step(self, count=1):
        # Hacky way of initializing without placing burden on caller.
        try: self.active
        except: self.initialize()

        for _ in xrange(count):
            # Step the environment.
            self.environment.step()
            self.time += 1
            print(self.time)
            if self.time % 100 == 0: print(self.time)

            # Activate neurons and wait for workers.
            if self.multithreaded:
                for i in xrange(len(self.active)):
                    self.active[i] = True
                while any(x == True for x in self.active): pass
            # If no other threads, do it yourself
            else: for neuron in self.neurons: neuron.step()

            # Activate drivers
            self.drive()

    def work(self, start_index, stop_index):
        while True:
            for neuron_id in xrange(start_index, stop_index):
                if self.active[neuron_id]:
                    self.neurons[neuron_id].step()
                    self.active[neuron_id] = False

    def create_neuron(self, base_current=0.0,
            neuron_type=NeuronTypes.GANGLION, probe_name=None):
        neuron = Neuron(
            neuron_id=len(self.neurons),
            base_current=base_current,
            neuron_type=neuron_type,
            environment=self.environment)
        self.neurons.append(neuron)
        if probe_name: neuron.set_probe(Probe())

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
            enzyme_concentration=1.0, axon_delay=0, dendrite_strength=25,
            active_molecules=[Molecule_IDs.GLUTAMATE], probe_name=None):
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

        # Set up probe.
        if probe_name: pass ## CHANGE ME
        return synapse

    def create_gap_junction(self, pre_neuron, post_neuron, conductance=1.0):
        Neuron.create_gap_junction(pre_neuron, post_neuron, conductance)

    def register_driver(self, neuron, driver, name=None):
        self.neuron_drivers[neuron] = driver
        self.drivers[name] = driver

    def get_driver_data(self, name):
        return (name, self.drivers[name].data)
