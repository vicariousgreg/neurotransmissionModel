# Neuron Factory
#
# The Neuron Factory is used to create and manage neurons and synapses.  It
#     holds the neuron environment and can easily simulate a timestep on all
#     components it holds.
#
# Drivers can be added to activate particular neurons at each timestep.

from math import ceil
from environment import Environment
from neuron import Neuron, NeuronTypes
from receptor import epsp

class NeuronFactory:
    def __init__(self):
        self.environment = Environment()
        self.neurons = []
        self.synapses = []

        self.drivers = {}
        self.neuron_drivers = {}

        self.time = 0

    def drive(self):
        # Activate drivers
        # Drivers do not step the neuron, but modify it to prepare for
        #     a timestep.  If True is returned, the neuron should be
        #     stepped during this timestep.
        for neuron,driver in self.neuron_drivers.iteritems():
            driver.drive(neuron, self.time)

    def step(self, count=1):
        for _ in xrange(count):
            # Activate drivers
            self.drive()

            # Step the environment
            self.environment.step()

            # Log time
            self.time += 1
            if True or self.time % 100 == 0: print(self.time)

            # Activate neurons
            for neuron in self.neurons: neuron.step(self.time)

    def create_neuron(self, base_current=0.0,
            neuron_type=NeuronTypes.GANGLION, record=False):
        neuron = Neuron(
            neuron_id=len(self.neurons),
            base_current=base_current,
            neuron_type=neuron_type,
            environment=self.environment,
            record=record)
        self.neurons.append(neuron)

        return neuron

    def create_neuron_grid(self, width, height, base_current=0.0,
            neuron_type=NeuronTypes.GANGLION, record=False):
        output = []
        for i in xrange(height):
            row = []
            for j in xrange(width):
                row.append(self.create_neuron(base_current, neuron_type, record=record))
            output.append(row)
        return output

    def connect_grids(self, grid1, grid2,
            receptor=epsp, delay=0, strength=25):
        h1,w1 = (len(grid1), len(grid1[0]))
        h2,w2 = (len(grid2), len(grid2[0]))

        if h1 != h2 or w1 != w1:
            raise ValueError

        '''
        for i in xrange(h1):
            for j in xrange(w1):
                self.create_synapse(grid1[i][j], grid2[i][[j],
                    transporter, receptor,
                    enzyme_concentration,
                    delay, strength)
        '''

    def create_synapse(self, pre_neuron, post_neuron,
            receptor=epsp, delay=0, strength=1):
        synapse = Neuron.create_synapse(pre_neuron, post_neuron,
            receptor=receptor, delay=delay, strength=strength)
        self.synapses.append(synapse)
        return synapse

    def create_gap_junction(self, pre_neuron, post_neuron, conductance=1.0):
        Neuron.create_gap_junction(pre_neuron, post_neuron, conductance)

    def register_driver(self, neuron, driver, name=None):
        self.neuron_drivers[neuron] = driver
        self.drivers[name] = driver

    def get_driver_data(self, name):
        return (name, self.drivers[name].data)
