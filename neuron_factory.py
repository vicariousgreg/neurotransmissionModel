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
from molecule import Transporters, Receptors, Molecule_IDs

class NeuronFactory:
    def __init__(self):
        self.neuron_environment = NeuronEnvironment()
        self.neurons = []
        self.synapses = []

        self.drivers = {}
        self.neuron_drivers = {}
        self.probes = {}
        self.neuron_probes = {}
        self.concentration_probes = {}

        self.tokens = set()
        self.time = 0
        self.stable = 0

    def step(self, count=1):
        for _ in xrange(count):
            new_tokens = set()

            # Activate drivers
            # Drivers do not step the neuron, but modify it to prepare for
            #     a timestep.  If True is returned, the neuron should be
            #     stepped during this timestep.
            for neuron,driver in self.neuron_drivers.iteritems():
                if driver.drive(neuron, self.time):
                    self.tokens.add(neuron.neuron_id)

            #if len(self.tokens) > 0: print(tuple(self.tokens))

            # Activate neurons with tokens
            for neuron_id in self.tokens:
                new_tokens.update(self.neurons[neuron_id].step())

            # Record neuron somas
            for neuron,probe in self.neuron_probes.iteritems():
                probe.record(neuron.soma)

            # Record components with probes
            for component,probe in self.concentration_probes.iteritems():
                probe.record(component)

            # Step the environment.
            if self.neuron_environment.step(): self.stable += 1
            self.time += 1
            self.tokens = new_tokens

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
        self.tokens.add(neuron.neuron_id)
        return neuron

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
        self.tokens.update((pre_neuron.neuron_id, post_neuron.neuron_id))

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
            neuron.adjust_activation(self.activation)
            return True
        else: return False

    def postdelay(self, neuron, time):
        neuron.adjust_activation(self.activation)
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
                neuron.adjust_activation(self.activation)
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
