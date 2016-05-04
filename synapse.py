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

from molecule import Molecules, Metabolizers, num_molecules
from enzyme import Enzymes, metabolize, num_enzymes
from random import gauss

class Synapse:
    def __init__(self, baseline_concentration=1.0, verbose=False):
        """
        A synapse contains a list of molecule concentrations by id and
            a list of enzyme concentrations by id.
        |baseline_concentration| is the intial enzyme concentration.
        """
        if baseline_concentration > 1.0: raise ValueError

        self.concentrations = [0.0] * num_molecules
        self.enzymes = [baseline_concentration] * num_enzymes
        self.verbose = verbose

    def step(self, time):
        """
        Runs a time step.
        Molecules are cleared from the synapse every time step.
        The amount cleared depends on the concentrations of molecules
            and their corresponding enzymes.
        """
        for mol_id,mol_count in enumerate(self.concentrations):
            enz_id,rate = Metabolizers[mol_id]
            enzyme_count = self.enzymes[enz_id]

            destroyed = metabolize(enzyme_count, mol_count, rate)
            self.concentrations[mol_id] -= \
                metabolize(enzyme_count, mol_count, rate)
            if self.verbose:
                print("Destroyed %f" % destroyed)
                print("Concentration: %f" % self.concentrations[mol_id])

    def insert(self, mol_count, mol_id=Molecules.GLUTAMATE):
        """
        Inserts |mol_count| molecules of the molecule specified by |mol_id|.
        """
        self.concentrations[mol_id] += mol_count

    def get(self, mol_id):
        """
        Retrieves a stochastic number of molecules with the given |mol_id|.
        The number of molecules returned is based on the concentration.
        Returns between 80 and 100 percent of the concentration.
        """
        #return min(self.concentrations[mol_id],
        #    gauss(0.5*self.concentrations[mol_id], 0.01))
        return self.concentrations[mol_id]

    def remove(self, mol_id, mol_count):
        """
        Removes |mol_count| molecules of the molecule specified by |mol_id|.
        """
        self.concentrations[mol_id] -= mol_count
