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

    def set_enzyme_concentration(self, e_c, molecules=range(len(Molecules))):
        for i in molecules:
            self.synaptic_cleft.enzymes[i] = e_c

    def step(self, time):
        """
        Runs a timestep, which involves the following steps:

        0. Environment cycles
        1. Axons release
        2. Dendrites and axons bind
        3. Dendrites release
        4. Enzymes metabolize
        5. Axons replenish
        """
        # 0: Cycle environment
        self.environment.step()

        # 1: Release from axons
        for axon in self.axons:
            axon.release(self.synaptic_cleft)

        # 2: Bind to dendrites and axons
        self.synaptic_cleft.bind(self.dendrites + self.axons)

        # 3: Release from dendrites
        for dendrite in self.dendrites:
            dendrite.release(self.synaptic_cleft)

        # 4: Metabolize
        self.synaptic_cleft.metabolize()

        # 5: Replenish
        for axon in self.axons:
            axon.replenish()

    def create_axon(self, **args):
        args["environment"] = self.environment
        axon = Axon(**args)
        self.axons.append(axon)
        return axon

    def create_dendrite(self, **args):
        args["environment"] = self.environment
        dendrite = Dendrite(**args)
        self.dendrites.append(dendrite)
        return dendrite
