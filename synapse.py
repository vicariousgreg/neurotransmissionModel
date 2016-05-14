# Synapse
#
# The synapse contains axons, dendrites, and a synaptic cleft.

from molecule import Enzymes
from axon import Axon
from dendrite import Dendrite
from synaptic_cleft import SynapticCleft
from environment import SynapseEnvironment

class Synapse:
    def __init__(self, initial_enzyme_concentration=0.0, verbose=False):
        """
        Creates a synapse with an initialized synaptic cleft.
        An initial enzyme concentration can be specified.
        """
        self.environment = SynapseEnvironment()

        self.synaptic_cleft = SynapticCleft(
            enzyme_concentration=initial_enzyme_concentration,
            environment=self.environment, verbose=verbose)
        self.axons = []
        self.dendrites = []

    def set_enzyme_concentration(self, e_c, enzymes=range(Enzymes.size)):
        """
        Sets the concentration of the given |enzymes| in the synaptic cleft.
        """
        for i in enzymes: self.synaptic_cleft.enzymes[i] = e_c

    def create_axon(self, **args):
        """
        Creates an axon and adds it to the synapse.
        """
        args["environment"] = self.environment
        axon = Axon(**args)
        self.axons.append(axon)
        return axon

    def create_dendrite(self, **args):
        """
        Creates a dendrite and adds it to the synapse.
        """
        args["environment"] = self.environment
        dendrite = Dendrite(**args)
        self.dendrites.append(dendrite)
        return dendrite

    def step(self, time):
        """
        Runs a timestep, which involves the following steps:

        1. Release bound molecules from dendrites and axons.
            These shouldn't stay here, but are there temporarily for the sake
                of interaction with the larger system.  May change later.
            Do not release native molecules from the axon!  They stay due to
                the fact that transporters pass them through, but do not pass
                reuptake inhibitors through.
        2. Cycle environment.
            This makes the previously released molecules available for
                computation during the time step.
            
        3. Release neurotransmitters from axons into synaptic cleft.
        4. Metabolize molecules in the synaptic cleft.
        5. Bind molecules to dendrite receptors and axon transporters
        6. Replenish axon neurotransmitter reserves
        7. Final environment cycle
        """
        # 1: Release from Dendrites
        for dendrite in self.dendrites:
            for mol_id,concentration in dendrite.unbind():
                self.synaptic_cleft.add_concentration(concentration,mol_id)

        # Release reuptake inhibitors from axons
        for axon in self.axons:
            for mol_id,concentration in axon.unbind():
                self.synaptic_cleft.add_concentration(concentration,mol_id)

        # 2: Cycle environment
        self.environment.step()

        # 3: Release from axons
        for axon in self.axons:
            released = axon.release()
            self.synaptic_cleft.add_concentration(
                released, mol_id=axon.native_mol_id)

        # 4: Metabolize
        self.synaptic_cleft.metabolize()

        # 5: Bind to dendrites and axons
        self.synaptic_cleft.bind(self.dendrites + self.axons)

        # 6: Replenish
        for axon in self.axons:
            axon.replenish()

        # 7. Cycle environment
        self.environment.step()

