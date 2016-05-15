# Synapse
#
# The synapse contains axons, dendrites, and a synaptic cleft.

from molecule import Enzymes
from axon import Axon
from dendrite import Dendrite
from synaptic_cleft import SynapticCleft
from environment import SynapseEnvironment

class Synapse:
    def __init__(self, initial_enzyme_concentration=0.0,
                    single_molecule=None, verbose=False):
        """
        Creates a synapse with an initialized synaptic cleft.
        An initial enzyme concentration can be specified.

        If a single molecule is provided, we assume that it is the only
            molecule that is passed through this synapse.  It is passed into
            the synaptic cleft constructor, which will set itself up to save
            time and space by only checking for that molecule.
        """
        self.environment = SynapseEnvironment()

        self.synaptic_cleft = SynapticCleft(
            enzyme_concentration=initial_enzyme_concentration,
            single_molecule = single_molecule,
            environment=self.environment, verbose=verbose)
        self.axon = None
        self.dendrites = []
        self.components = [self.synaptic_cleft]

        self.active = True

    def set_enzyme_concentration(self, e_c, enzymes=range(Enzymes.size)):
        """
        Sets the concentration of the given |enzymes| in the synaptic cleft.

        If the synapse is single molecule, then we can ignore |enzymes| and
            simply set the concentration.
        """
        if self.synaptic_cleft.single_molecule is not None:
            self.synaptic_cleft.enzymes = e_c
        else:
            for i in enzymes: self.synaptic_cleft.enzymes[i] = e_c

    def create_axon(self, **args):
        """
        Creates an axon and adds it to the synapse.
        """
        args["environment"] = self.environment
        axon = Axon(**args)
        self.axon = axon
        self.components.append(axon)
        return axon

    def create_dendrite(self, **args):
        """
        Creates a dendrite and adds it to the synapse.
        """
        args["environment"] = self.environment
        dendrite = Dendrite(**args)
        self.dendrites.append(dendrite)
        self.components.append(dendrite)
        return dendrite

    def step(self, time):
        """
        Runs a timestep, which involves the following steps:

        1. Release bound molecules from dendrites and axon.
            These shouldn't stay here, but are there temporarily for the sake
                of interaction with the larger system.  May change later.
            Do not release native molecules from the axon!  They stay due to
                the fact that transporters pass them through, but do not pass
                reuptake inhibitors through.
        2. Cycle environment.
            This makes the previously released molecules available for
                computation during the time step.
            
        3. Release neurotransmitters from axon into synaptic cleft.
        4. Metabolize molecules in the synaptic cleft.
        5. Bind molecules to dendrite receptors and axon transporters
        6. Replenish axon neurotransmitter reserves
        7. Final environment cycle
        """
        changed = False
        if self.active:
            # 1: Release from Dendrites
            for dendrite in self.dendrites:
                for mol_id,concentration in dendrite.unbind():
                    self.synaptic_cleft.add_concentration(concentration,mol_id)

            # Release reuptake inhibitors from axon
            try:
                for mol_id,concentration in self.axon.unbind():
                    self.synaptic_cleft.add_concentration(concentration,mol_id)
            except AttributeError: pass

            changed = changed or self.environment.dirty
            # 2: Cycle environment
            self.environment.step()

        # 3: Release from axon
        try:
            #if self.axon.releasing:
            released = self.axon.release()
            if released > 0.0:
                self.synaptic_cleft.add_concentration(
                    released, mol_id=self.axon.native_mol_id)
        except AttributeError: pass

        changed = changed or self.environment.dirty

        if self.active:
            # 4: Metabolize
            self.synaptic_cleft.metabolize()

            # 5: Bind to dendrites and axon
            if self.axon:
                self.synaptic_cleft.bind(self.dendrites + [self.axon])
            else:
                self.synaptic_cleft.bind(self.dendrites)

            # 6: Replenish
            try: self.axon.replenish()
            except AttributeError: pass

            changed = changed or self.environment.dirty

        # 7. Cycle environment
        self.environment.step()

        self.active = changed

