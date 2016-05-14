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

from environment import NeuronEnvironment
from neuron import Neuron, NeuronTypes
from molecule import Transporters, Receptors

class NeuronFactory:
    def __init__(self):
        self.neuron_environment = NeuronEnvironment()
        self.neurons = []
        self.synapses = []
        self.drivers = {}

        self.probes = {}
        self.neuron_probes = {}

        self.base_driver = ConstantDriver(0.0)
        self.time = 0

    def step(self, count=1):
        for _ in xrange(count):
            for neuron in self.neurons:
                try: self.neuron_probes[neuron].record(neuron.soma)
                except KeyError: pass
                self.drivers.get(neuron, self.base_driver).drive(neuron, self.time)
            for synapse in self.synapses: synapse.step(self.time)
            self.neuron_environment.step()
            self.time += 1

    def create_neuron(self, base_current=0.0, neuron_type=NeuronTypes.GANGLION,
                              probe_name=None):
        neuron = Neuron(base_current=base_current,
            neuron_type=neuron_type,
            environment=self.neuron_environment)
        self.neurons.append(neuron)
        if probe_name:
            probe = VoltageProbe()
            self.probes[probe_name] = probe
            self.neuron_probes[neuron] = probe
        return neuron

    def create_synapse(self, pre_neuron, post_neuron,
            transporter=Transporters.GLUTAMATE, receptor=Receptors.AMPA,
            axon_delay=None, dendrite_strength=0.05):
        synapse = Neuron.create_synapse(pre_neuron, post_neuron,
            transporter=transporter, receptor=receptor,
            axon_delay=axon_delay, dendrite_strength=dendrite_strength)
        self.synapses.append(synapse)
        return synapse

    def create_gap_junction(self, pre_neuron, post_neuron, conductance=1.0):
        Neuron.create_gap_junction(pre_neuron, post_neuron, conductance)

    def register_driver(self, neuron, driver):
        self.drivers[neuron] = driver

    def get_probe_data(self, name):
        return (name, self.probes[name].data)

class ConstantDriver:
    def __init__(self, activation=0.0):
        self.activation = activation

    def drive(self, neuron, time):
        neuron.step(self.activation)

class CurrentPulseDriver:
    def __init__(self, current=0.0, period=1000, length=500):
        self.current = current
        self.period = period
        self.length = length

    def drive(self, neuron, time):
        if time % self.period == 0:
            neuron.soma.iapp = self.current
        elif time % self.period == self.length:
            neuron.soma.iapp = 0.0
        neuron.step()

class ActivationPulseDriver:
    def __init__(self, activation=0.0, period=1000, length=1, decrement=None):
        self.activation = activation
        self.period = period
        self.length = length
        self.decrement = decrement

    def drive(self, neuron, time):
        if time % self.period < self.length:
            neuron.step(self.activation)
            if self.decrement and self.activation > 0.0:
                self.activation -= self.decrement
        else:
            neuron.step()

class VoltageProbe:
    def __init__(self):
        self.data = []

    def record(self, component):
        self.data.append(component.get_scaled_voltage())

class ConcentrationProbe:
    def __init__(self): pass
