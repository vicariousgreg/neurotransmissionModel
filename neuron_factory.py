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
        self.concentration_probes = {}

        self.base_driver = ConstantDriver(0.0)
        self.time = 0

    def step(self, count=1):
        for _ in xrange(count):
            for neuron in self.neurons:
                try: self.neuron_probes[neuron].record(neuron.soma)
                except KeyError: pass
                self.drivers.get(neuron, self.base_driver).drive(neuron, self.time)
            for synapse in self.synapses:
                for component in synapse.components:
                    try: self.concentration_probes[component].record(component)
                    except KeyError: pass
                synapse.step(self.time)
            self.neuron_environment.step()
            self.time += 1

    def create_neuron(self, base_current=0.0,
            neuron_type=NeuronTypes.GANGLION, probe_name=None):
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
            enzyme_concentration=1.0,
            axon_delay=None, dendrite_strength=0.05, single_molecule=True,
            axon_probe_name=None, cleft_probe_name=None, dendrite_probe_name=None):
        # If single molecule is true, the synapse will save time and space by
        #     assuming that only one molecule will move through it.  This means
        #     that the proteins must use the same native molecule, and no
        #     exogenous molecules can be admitted into the synapse.
        if single_molecule:
            # First, we must validate that the proteins use the same molecule.
            if transporter.native_mol_id != receptor.native_mol_id:
                raise ValueError
            # Set the molecule.
            molecule = transporter.native_mol_id
        # Otherwise, set the molecule to none.
        else: molecule = None

        # Create synapse.
        synapse = Neuron.create_synapse(pre_neuron, post_neuron,
            transporter=transporter, receptor=receptor,
            single_molecule = molecule, enzyme_concentration=enzyme_concentration,
            axon_delay=axon_delay, dendrite_strength=dendrite_strength)
        self.synapses.append(synapse)

        # Set up probes.
        if axon_probe_name:
            axon = synapse.axons[0]
            probe = ConcentrationProbe(axon.native_mol_id)
            self.concentration_probes[axon] = probe
            self.probes[axon_probe_name] = probe
        if cleft_probe_name:
            cleft = synapse.synaptic_cleft
            probe = ConcentrationProbe(synapse.axons[0].native_mol_id)
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
    def __init__(self, mol_id):
        self.data = []
        self.mol_id = mol_id

    def record(self, component):
        self.data.append(component.get_concentration(self.mol_id))
