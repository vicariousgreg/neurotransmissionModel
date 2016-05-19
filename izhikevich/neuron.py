# Neuron Model

from multiprocessing import Value
from enum import enum
from soma import Soma
from synapse import Synapse
from molecule import Transporters, Receptors
from photoreceptor import PhotoreceptorSoma

NeuronTypes = enum(
    PHOTORECEPTOR = 0,
    GANGLION = 1
)

class Neuron:
    def __init__(self, neuron_id=None, base_current=0.0,
                    neuron_type=NeuronTypes.GANGLION, environment=None):
        self.environment = environment
        self.neuron_id = neuron_id

        # Soma and axon threshold
        if neuron_type == NeuronTypes.PHOTORECEPTOR:
            self.soma = PhotoreceptorSoma(environment)
            self.axon_threshold = -9999
        elif neuron_type == NeuronTypes.GANGLION:
            self.soma = Soma(base_current, environment)
            self.axon_threshold = -55.0

        # Inputs
        self.dendrites = []
        self.external_activation = Value('d', 0.0)
        self.internal_activation = 0.0
        self.gap_junctions = []
        self.active_gap_junctions = False

        # Outputs
        self.axons = []
        self.synapses = []

        # Active flags
        self.soma_stable = False
        self.synapses_stable = []

    def external_activate(self, delta):
        self.external_activation.value += delta

    def internal_activate(self, delta):
        self.internal_activation += delta

    def step(self, resolution=100):
        soma_voltage = self.soma.get_voltage()

        # Check gap junctions if active
        if self.active_gap_junctions:
            gap_current = 0
            for other,conductance in self.gap_junctions:
                df = conductance*(other.soma.get_voltage() - soma_voltage)
                gap_current += df

            # Destabilize soma if new current is significantly different
            if abs(gap_current - self.soma.gap_current) > 0.001:
                self.soma_stable = False
                self.soma.gap_current = gap_current

        # Activate the neuron from each dendrite
        # This will check the receptor type and decide how to modify the neuron
        for dendrite in self.dendrites:
            dendrite.activate(self)

        activation = self.external_activation.value + self.internal_activation

        # Activate the soma
        if activation != 0.0 or not self.soma_stable:
            self.soma_stable = self.soma.step(activation, resolution=resolution)

        # Activate the axons
        # If they are releasing, their synapse should be activated
        if soma_voltage < self.axon_threshold: soma_voltage = None
        for i,axon in enumerate(self.axons):
            if not axon.step(self.soma.firing):
                self.synapses_stable[i] = False

        # Cycle synapses if active.
        for i,synapse in enumerate(self.synapses):
            if not self.synapses_stable[i]:
                s = synapse.step()
                self.synapses_stable[i] = s

        # Reset activation and return set of active neurons
        self.external_activation.value = 0.0
        self.internal_activation = 0.0

    def apply_current(self, current):
        self.soma.current = current
        self.soma_stable = False

    @staticmethod
    def create_synapse(presynaptic, postsynaptic, active_molecules=None,
            transporter=Transporters.GLUTAMATE, receptor=Receptors.AMPA,
            enzyme_concentration=1.0,
            axon_delay=0, dendrite_strength=0.0015):
        synapse = Synapse(
            postsynaptic_id=postsynaptic.neuron_id,
            initial_enzyme_concentration=enzyme_concentration,
            active_molecules=active_molecules)
        axon = synapse.create_axon(
                    transporter=transporter,
                    replenish_rate=0.1,
                    reuptake_rate=0.5,
                    capacity=1.0,
                    delay=axon_delay)
        dendrite = synapse.create_dendrite(
                    receptor=receptor,
                    density=0.25,
                    strength=dendrite_strength)

        presynaptic.axons.append(axon)
        presynaptic.synapses.append(synapse)
        presynaptic.synapses_stable.append(True)
        postsynaptic.dendrites.append(dendrite)
        return synapse

    @staticmethod
    def create_gap_junction(presynaptic, postsynaptic, conductance):
        presynaptic.gap_junctions.append((postsynaptic,conductance))
        postsynaptic.gap_junctions.append((presynaptic,conductance))
        presynaptic.active_gap_junctions = True
        postsynaptic.active_gap_junctions = True
