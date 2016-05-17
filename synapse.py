# Synapse
#
# The synapse contains axons, dendrites, and a synaptic cleft.

from molecule import Enzymes, Molecule_IDs
from axon import Axon
from dendrite import Dendrite
from synaptic_cleft import SynapticCleft
from environment import SynapseEnvironment

class Synapse:
    def __init__(self, postsynaptic_id=None, initial_enzyme_concentration=0.0,
                    active_molecules=[Molecule_IDs.GLUTAMATE], verbose=False):
        """
        Creates a synapse with an initialized synaptic cleft.
        An initial enzyme concentration can be specified.

        If a single molecule is provided, we assume that it is the only
            molecule that is passed through this synapse.  It is passed into
            the synaptic cleft constructor, which will set itself up to save
            time and space by only checking for that molecule.
        """
        self.environment = SynapseEnvironment()
        self.postsynaptic_id = postsynaptic_id

        self.synaptic_cleft = SynapticCleft(
            enzyme_concentration=initial_enzyme_concentration,
            active_molecules = active_molecules,
            environment=self.environment, verbose=verbose)
        self.axon = None
        self.dendrites = []
        self.components = [self.synaptic_cleft]

    def set_enzyme_concentration(self, e_c, enzymes=range(Enzymes.size)):
        """
        Sets the concentration of the given |enzymes| in the synaptic cleft.
        """
        for i in enzymes: self.synaptic_cleft.enzymes[i] = e_c

    def create_axon(self, **args):
        """
        Creates an axon and adds it to the synapse.
        """
        axon = Axon(**args)
        self.axon = axon
        self.components.append(axon)
        return axon

    def create_dendrite(self, **args):
        """
        Creates a dendrite and adds it to the synapse.
        """
        dendrite = Dendrite(**args)
        self.dendrites.append(dendrite)
        self.components.append(dendrite)
        return dendrite

    def step(self):
        """
        Runs a timestep, which involves the following steps:

        1. Release neurotransmitters from axon into synaptic cleft.
        2. Step synaptic cleft.  This involves two steps:
              - Metabolize molecules in the synaptic cleft.
              - Bind molecules to dendrite receptors and axon transporters
        3. Cycle environment

        Returns return of stepping environment, which is the stability of
            the synapse (False if environment changed, else True).
        """

        # 1: Release from axon
        try:
            released = self.axon.release()
            if released > 0.0:
                self.synaptic_cleft.add_concentration(
                    released, mol_id=self.axon.native_mol_id)
        except AttributeError: pass

        # 2: Step synaptic cleft
        self.synaptic_cleft.step(dendrites=self.dendrites, axon=self.axon)

        # 4. Cycle environment
        return self.environment.step()# and all(dendrite.bound == 0.0 for dendrite in self.dendrites)
