# Neuron Model

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
    def __init__(self, base_current=0.0, neuron_type=NeuronTypes.GANGLION, environment=None):
        if neuron_type == NeuronTypes.PHOTORECEPTOR:
            self.soma = PhotoreceptorSoma(environment)
        elif neuron_type == NeuronTypes.GANGLION:
            self.soma = Soma(base_current, environment)
        self.axons = []
        self.dendrites = []
        self.gap_junctions = []
        self.active_gap_junctions = False
        self.environment = environment

    def step(self, activation=0.0, resolution=100):
        # Activate gap junctions
        gap_current = 0
        soma_voltage = self.soma.get_voltage()

        # Check gap junctions.
        gap_current_changed = False
        if self.active_gap_junctions:
            for other,conductance in self.gap_junctions:
                df = conductance*(other.soma.get_voltage() - soma_voltage)
                gap_current += df

            if abs(gap_current - self.soma.gap_current) > 0.001:
                gap_current_changed = True
                self.soma.gap_current = gap_current

        # Gather input from dendrites.
        # TODO: Implement different activations based on dendrite
        #         - add a function to each receptor protein that takes
        #             the neuron and does something to it
        for dendrite in self.dendrites:
            activation += dendrite.get_activation()

        # Activate the soma
        if activation > 0.0 or not self.soma.stable or gap_current_changed:
            self.soma.step(activation, resolution=resolution)

        # Activate the axons
        for axon in self.axons:
            axon.step(voltage = soma_voltage, resolution=resolution)

    @staticmethod
    def create_synapse(presynaptic, postsynaptic, single_molecule=None,
            transporter=Transporters.GLUTAMATE, receptor=Receptors.AMPA,
            enzyme_concentration=1.0,
            axon_delay=None, dendrite_strength=0.05):
        synapse = Synapse(initial_enzyme_concentration=enzyme_concentration,
                                             single_molecule=single_molecule)
        axon = synapse.create_axon(
                    transporter=transporter,
                    replenish_rate=0.1,
                    reuptake_rate=0.5,
                    capacity=1.0,
                    delay=axon_delay)
        dendrite = synapse.create_dendrite(
                    single_molecule=single_molecule,
                    receptor=receptor,
                    density=0.05,
                    strength=dendrite_strength)

        presynaptic.axons.append(axon)
        postsynaptic.dendrites.append(dendrite)
        return synapse

    @staticmethod
    def create_gap_junction(presynaptic, postsynaptic, conductance):
        presynaptic.gap_junctions.append((postsynaptic,conductance))
        postsynaptic.gap_junctions.append((presynaptic,conductance))
        presynaptic.active_gap_junctions = True
        postsynaptic.active_gap_junctions = True
