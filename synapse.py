# Synapse Model
#
# Models the space between neurons, including concentration of various
#     neurotransmitters, their corresponding enzymes, and the metabolic
#     processes that affect neurotransmitter concentration.
#
# Presynpatic neurons pump neurotransmitters into the synapse.
#
# Synaptic neurotransmitters bind stochastically to postsynaptic neuron
#     receptors.

from molecule import Molecules, Metabolizers
from enzyme import Enzymes, metabolize

class Synapse:
    def __init__(self):
        """
        A synapse contains a list of molecule concentrations by id and
            a list of enzyme concentrations by id.
        """
        self.concentrations = [0] * len(Molecules)
        self.enzymes = [0] * len(Enzymes)

    def step(self):
        """
        Runs a time step.
        Molecules are cleared from the synapse every time step.
        The amount cleared depends on the concentrations of molecules
            and their corresponding enzymes.
        """
        for mol_id,mol_count in enumerate(self.concentrations):
            enz_id,rate = Metabolizers[mol_id]
            enzyme_count = self.enzymes[enz_id]

            self.concentrations[mol_id] -= \
                metabolize(enzyme_count, mol_count, rate)

    def insert(self, mol_id, count):
        """
        Inserts |count| molecules of the molecule specified by |mol_id|.
        """
        self.concentrations[mol_id] += count

    def get(self, mol_id):
        """
        Retrieves a stochastic number of molecules with the given |mol_id|.
        The number of molecules returned is based on the concentration.
        Returns between 80 and 100 percent of the concentration.
        """
        return self.concentrations[mol_id] * (1 - (random.random() * 0.2))
