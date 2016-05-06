# Synaptic Cleft Model
#
# Models the space between neurons, including concentration of various
#     neurotransmitters, their corresponding enzymes, and the metabolic
#     processes that affect neurotransmitter concentration.
#
# Presynpatic neurons pump neurotransmitters into the synaptic cleft.
#
# Synaptic neurotransmitters bind stochastically to postsynaptic neuron
#     receptors.

from molecule import Molecules, Enzymes, Metabolizers, metabolize
from pool import Pool
from membrane import stochastic_bind

class SynapticCleft:
    def __init__(self, enzyme_concentration=1.0, environment=None, verbose=False):
        """
        A synaptic cleft contains a list of molecule concentrations by id and
            a list of enzyme concentrations by id.
        |enzyme_concentration| is the intial enzyme concentration.
        """
        if enzyme_concentration > 1.0: raise ValueError

        self.pools = [Pool(environment=environment) for m in xrange(Molecules.size)]
        self.enzymes = [enzyme_concentration] * Enzymes.size
        self.verbose = verbose

        self.receptors = [[]] * Enzymes.size

    def get_concentration(self, mol_id=Molecules.GLUTAMATE):
        return self.pools[mol_id].get_concentration()

    def set_concentration(self, new_concentration, mol_id=Molecules.GLUTAMATE):
        return self.pools[mol_id].set_concentration(new_concentration)

    def add_concentration(self, molecules, mol_id=Molecules.GLUTAMATE):
        return self.pools[mol_id].add_concentration(molecules)

    def remove_concentration(self, molecules, mol_id=Molecules.GLUTAMATE):
        return self.pools[mol_id].remove_concentration(molecules)

    def connect(self, receptor):
        receptor.destination = self
        self.receptors[receptor.mol_id].append(receptor)

    def step(self, time):
        """
        Runs a time step.
        Molecules are cleared from the synaptic cleft every time step.
        The amount cleared depends on the concentrations of molecules
            and their corresponding enzymes.
        """
        # Distribute molecules to available membrane receptors.
        for mol_id in xrange(Molecules.size):
            receptors = self.receptors[mol_id]
            empty_densities = [receptor.get_available_spots() for receptor in receptors]
            total_empty_density = sum(empty_densities)

            if total_empty_density == 0.0: continue

            available = self.get_concentration(mol_id)

            for empty_density,receptor in zip(empty_densities, receptors):
                portion = available * (empty_density / total_empty_density)
                bound = stochastic_bind(portion, empty_density)
                receptor.add_concentration(bound)
                self.remove_concentration(bound)

        # Metabolize from remaining pool.
        for mol_id,mol_count in enumerate(self.get_concentration(mol) for mol in xrange(Molecules.size)):
            if mol_count == 0.0: continue
            enz_id,rate = Metabolizers[mol_id]
            enzyme_count = self.enzymes[enz_id]

            destroyed = metabolize(enzyme_count, mol_count, rate)
            self.remove_concentration(destroyed, mol_id)
            if self.verbose:
                print("Destroyed %f" % destroyed)
                print("Concentration: %f" % self.get_concentration(mol_id))
