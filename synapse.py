# Synapse
#
# The synapse contains axons, dendrites, and a synaptic cleft.

from molecule import Molecules
from axon import Axon
from dendrite import Dendrite
from synaptic_cleft import SynapticCleft
from environment import Environment, BatchEnvironment

class Synapse:
    def __init__(self, verbose=False):
        self.environment = BatchEnvironment()
        self.synaptic_cleft = SynapticCleft(
            enzyme_concentration=0.0, environment=self.environment, verbose=verbose)
        self.axons = []
        self.dendrites = []

    def set_enzyme_concentration(self, e_c, molecules=range(Molecules.size)):
        for i in molecules:
            self.synaptic_cleft.enzymes[i] = e_c

    def step(self, time):
        self.environment.step(time)
        for axon in self.axons:
            axon.step(time)
        self.synaptic_cleft.step(time)
        for dendrite in self.dendrites:
            dendrite.step(time)

    def create_axon(self, **args):
        args["environment"] = self.environment
        axon = Axon(**args)
        self.axons.append(axon)
        self.synaptic_cleft.connect(axon)
        return axon

    def create_dendrite(self, **args):
        args["environment"] = self.environment
        dendrite = Dendrite(**args)
        self.dendrites.append(dendrite)
        self.synaptic_cleft.connect(dendrite)
        return dendrite
