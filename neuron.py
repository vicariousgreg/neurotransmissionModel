# Neuron Model

from soma import Soma
from synapse import Synapse
from molecule import Transporters, Receptors

class Neuron:
    def __init__(self, base_current=0.0):
        self.soma = Soma(base_current)
        self.axons = []
        self.dendrites = []
        self.gap_junctions = []

    def step(self, activation=0.0, resolution=100):
        # Activate gap junctions
        gap_current = 0
        for other,conductance in self.gap_junctions:
            df = conductance*(other.soma.v - self.soma.v)
            gap_current += df
        self.soma.gap_current = gap_current

        # Gather input from dendrites.
        # TODO: Implement different activations based on dendrite
        #         - add a function to each receptor protein that takes
        #             the neuron and does something to it
        for dendrite in self.dendrites:
            activation += 0.05*dendrite.get_concentration()

        # Activate the soma
        self.soma.step(activation, resolution=resolution)

        # Activate the axons
        for axon in self.axons:
            axon.step(voltage = self.soma.v, resolution=resolution)

    @staticmethod
    def create_synapse(presynaptic, postsynaptic,
            transporter=Transporters.GLUTAMATE, receptor=Receptors.AMPA):
        synapse = Synapse()
        axon = synapse.create_axon(
                    transporter=transporter,
                    replenish_rate=0.1,
                    reuptake_rate=0.5,
                    capacity=1.0)
        dendrite = synapse.create_dendrite(
                    receptor=receptor,
                    density=0.05)
        synapse.set_enzyme_concentration(1.0)

        presynaptic.axons.append(axon)
        postsynaptic.dendrites.append(dendrite)
        return synapse

    @staticmethod
    def create_gap_junction(presynaptic, postsynaptic, conductance):
        presynaptic.gap_junctions.append((postsynaptic,conductance))
        postsynaptic.gap_junctions.append((presynaptic,conductance))
