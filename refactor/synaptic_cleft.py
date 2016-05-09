# Synaptic Cleft Model
#
# Models the space between neurons, including concentration of various
#     neurotransmitters, their corresponding enzymes, and the metabolic
#     processes that affect neurotransmitter concentration.
#
# Presynpatic neurons pump neurotransmitters into the synaptic cleft.
#
# Synaptic neurotransmitters bind stochastically to postsynaptic neuron
#     receptors and presynaptic transporters.

from molecule import Molecules, Enzymes, metabolize
from pool_cluster import PoolCluster

class SynapticCleft(PoolCluster):
    def __init__(self, enzyme_concentration=1.0, environment=None, verbose=False):
        """
        A synaptic cleft contains pools of molecules and enzymes.
        |enzyme_concentration| is the intial concentration of enzymes.
        """
        PoolCluster.__init__(self,
            dict([(mol.mol_id, 0.0) for mol in Molecules]),
            environment)
        self.enzymes = [enzyme_concentration] * Enzymes.size
        self.verbose = verbose

    def step(self):
        self.metabolize()
        self.bind()

    def bind(self, membranes):
        """
        Bound/Unbound fraction
        f = [L] / ( [L] + K_d )
        """
        # Total concentration of each molecule
        mol_concentrations = dict()
        # Total density of proteins receptive to each molecule
        mol_protein_count = dict()
        # Total concentration of molecules receptive to each protein
        protein_mol_count = dict()

        # Check available molecules
        for mol_id, pool_id in self.pool_ids.iteritems():
            concentration = self.get_concentration(mol_id)
            if concentration == 0.0: continue
            mol_concentrations[mol_id] = concentration
            mol_protein_count[mol_id] = 0.0

        # Calculate densities of all proteins.
        for membrane in membranes:
            if membrane.density == 0.0: continue

            # Register protein and its receptive molecules
            # Factor in affinity
            protein_mol_count[membrane.protein] = 0.0
            for mol_id,affinity in membrane.protein.affinities.iteritems():
                if mol_id in mol_protein_count:
                    mol_protein_count[mol_id] += membrane.get_available_proteins(mol_id) * affinity
                    protein_mol_count[membrane.protein] += mol_concentrations[mol_id] * affinity

        mol_bound = dict([(mol_id, 0.0) for mol_id in mol_concentrations])

        # Compute for each protein-molecule pair.
        for membrane in membranes:
            protein = membrane.protein

            # How many molecules are competing for this protein?
            # Relative concentration:
            try: competing_molecules = protein_mol_count[protein]
            except KeyError: continue

            # For each receptive molecule:
            for mol_id,affinity in protein.affinities.iteritems():
                if mol_id not in mol_concentrations: continue

                count = membrane.get_available_proteins(mol_id)
                mol_concentration = mol_concentrations[mol_id]

                # Proportion of molecule relative to competitors.
                mol_fraction = affinity * mol_concentration / competing_molecules

                # Proportion of protein relative to competitors.
                protein_fraction = affinity * count / mol_protein_count[mol_id]

                k = (1 - mol_fraction * protein_fraction)
                bound = count * (mol_concentration**2) / ( mol_concentration + k )
                if self.verbose:
                    print(" P: %f      M: %f" % (count, mol_concentration))
                    print("fP: %f    fM: %f" % (protein_fraction, mol_fraction))
                    print("k: %f    bound: %f" % (k, bound))

                for membrane in membranes:
                    if membrane.protein == protein:
                        membrane.add_concentration(bound, mol_id)
                        mol_bound[mol_id] += bound
        for mol_id,bound in mol_bound.iteritems():
            self.remove_concentration(bound, mol_id)
            if self.verbose: print(self.get_concentration(mol_id))
        if self.verbose:
            print("")
            #raw_input()

    def metabolize(self):
        """
        Stochastically metabolizes molecules in the pools according to the
            concentration of appropriate enzymes.
        """
        for mol in Molecules:
            mol_count = self.get_concentration(mol.mol_id)
            if mol_count <= 0.0: continue

            mol_id = mol.mol_id
            enz_id = mol.enzyme_id
            rate = mol.metab_rate
            enzyme_count = self.enzymes[enz_id]

            destroyed = metabolize(enzyme_count, mol_count, rate, self.environment)
            self.remove_concentration(destroyed, mol_id)
            if self.verbose:
                print("Destroyed %f of %s" % (destroyed, mol.name))
                print("New concentrations: %f" % self.get_concentration(mol_id))
