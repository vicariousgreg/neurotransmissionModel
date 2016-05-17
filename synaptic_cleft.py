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
    def __init__(self, enzyme_concentration=1.0, single_molecule=None,
                                        environment=None, verbose=False):
        """
        A synaptic cleft contains pools of molecules and enzymes.
        |enzyme_concentration| is the intial concentration of enzymes.
        If |single_molecule| is provided, the synaptic cleft will assume that
            only that molecule will be introduced into the synapse.  This saves
            a lot of computation.
        """
        # If single molecule is indicated, set up functions and pool for time
        #     and space efficiency.
        self.single_molecule = single_molecule
        if single_molecule is not None:
            PoolCluster.__init__(self,
                dict([(single_molecule, 0.0)]),
                environment)
            self.bind = self.simple_bind
            mol = Molecules[single_molecule]
            self.enzymes = enzyme_concentration
            self.metabolize = lambda: self.metabolize_molecule(\
                single_molecule, self.enzymes, mol.metab_rate)
        else:
            PoolCluster.__init__(self,
                dict([(mol.mol_id, 0.0) for mol in Molecules]),
                environment)
            self.bind = self.complex_bind
            self.enzymes = [enzyme_concentration] * Enzymes.size
            self.metabolize = self.complex_metabolize
        self.verbose = verbose

    def step(self, dendrites, axon=None):
        self.metabolize()
        self.bind(dendrites, axon)

    def simple_bind(self, dendrites, axon=None):
        """
        Bound/Unbound fraction
        f = [L] / ( [L] + K_d )

        f is the fraction of molecules that are bound to receptors.
        L is the molecule concentration
        K_d is the dissociation constant

        This simpler version is less computationally expensive, but only works
            if the synaptic cleft contains only one molecule.
        """
        mol_id = self.single_molecule
        mol_concentration = self.get_concentration(mol_id)
        if mol_concentration <= 0.0:
            for dendrite in dendrites: dendrite.set_bound(0.0)
            return

        # Map of molecules to total concentrations of receptive proteins
        protein_counts = dict()
        total_protein_count = 0.0

        # Calculate densities of all proteins.
        for dendrite in dendrites:
            if dendrite.density == 0.0: continue
            count,affinity = (dendrite.density, dendrite.affinities[mol_id])
            protein_counts[dendrite] = count*affinity
            total_protein_count += count*affinity

        try:
            native_mol_id = axon.native_mol_id
            axon_available = min(axon.density, axon.capacity-axon.get_concentration(native_mol_id))
            if axon_available > 0.0:
                count,affinity = (axon_available, axon.affinities[native_mol_id])
                protein_count = count*affinity
                total_protein_count += protein_count

                # Proportion of protein relative to competitors.
                protein_fraction = protein_count / total_protein_count

                # Calculate bound concentration.
                k = (1 - (affinity*protein_fraction))
                bound = protein_count * (mol_concentration**2) / ( mol_concentration + k )

                # Transfer molecules to axon.
                axon.add_concentration(bound)
                self.remove_concentration(bound, native_mol_id)
        except AttributeError: pass

        # Compute for each dendrite.
        for dendrite,protein_count in protein_counts.iteritems():
            protein_count = protein_counts[dendrite]

            # Proportion of protein relative to competitors.
            protein_fraction = protein_count / total_protein_count

            # Calculate bound concentration.
            k = (1 - (affinity*protein_fraction))
            bound = protein_count * (mol_concentration**2) / ( mol_concentration + k )

            # Acivate dendrite.
            dendrite.set_bound(bound)

            if self.verbose:
                print("Concentrations:")
                print(" P: %f      M: %f" % (protein_count, mol_concentration))
                print("Proportions::")
                print("fP: %f" % protein_fraction)
                print("Constant and final bound count:")
                print("k: %f    bound: %f" % (k, bound))
                print("")

    def complex_bind(self, dendrites, axon=None):
        """
        Bound/Unbound fraction
        f = [L] / ( [L] + K_d )

        f is the fraction of molecules that are bound to receptors.
        L is the molecule concentration
        K_d is the dissociation constant

        The adapted version of this equation takes into account competition
            between similar receptors and similar molecules.
        """
        # Total concentration of each molecule
        mol_concentrations = dict()
        # Map of molecules to total concentrations of receptive proteins
        mol_protein_count = dict()
        # Map of proteins to total concentration of receptive molecules
        protein_mol_count = dict()

        # Check available molecules
        for mol_id, pool_id in self.pool_ids.iteritems():
            concentration = self.get_concentration(mol_id)
            if concentration == 0.0: continue
            mol_concentrations[mol_id] = concentration
            mol_protein_count[mol_id] = 0.0

        if len(mol_concentrations) == 0: return

        # Calculate densities of all proteins.
        for dendrite in dendrites:
            if dendrite.density == 0.0: continue

            # Register protein and its receptive molecules
            # Factor in affinity
            protein_mol_count[dendrite.protein] = 0.0
            for mol_id,affinity in dendrite.protein.affinities.iteritems():
                if mol_id in mol_protein_count:
                    mol_protein_count[mol_id] += dendrite.density * affinity
                    protein_mol_count[dendrite.protein] += mol_concentrations[mol_id] * affinity

        # Axon
        try:
            native_mol_id = axon.native_mol_id
            axon_available = min(axon.density, axon.capacity-axon.get_concentration(native_mol_id))
            if axon_available > 0.0:
                count,affinity = (axon_available, axon.affinities[native_mol_id])
                protein_count = count*affinity

                # Register protein and its receptive molecules
                # Factor in affinity
                protein_mol_count[axon.protein] = 0.0
                for mol_id,affinity in axon.protein.affinities.iteritems():
                    if mol_id in mol_protein_count:
                        mol_protein_count[mol_id] += axon_available * affinity
                        protein_mol_count[axon.protein] += mol_concentrations[mol_id] * affinity

                # Check if native molecule is present.
                mol_concentration = mol_concentrations[native_mol_id]

                competing_proteins = mol_protein_count[native_mol_id]
                if competing_proteins > 0:
                    # How many molecules are competing for this protein?
                    competing_molecules = protein_mol_count[axon.protein]

                    # Proportion of molecule relative to competitors.
                    mol_fraction = affinity * mol_concentration / competing_molecules

                    # Proportion of protein relative to competitors.
                    protein_fraction = protein_count / competing_proteins

                    # Calculate bound concentration.
                    k = (1 - (mol_fraction * protein_fraction * mol_fraction))
                    bound = protein_count * (mol_concentration**2) / ( mol_concentration + k )

                    # Transfer molecules.
                    axon.add_concentration(bound, mol_id)
                    self.remove_concentration(bound, mol_id)
        except KeyError: pass
        except AttributeError: pass

        # Compute for each protein-molecule pair.
        for dendrite in dendrites:
            dendrite.set_bound(0)

            # How many molecules are competing for this protein?
            try: competing_molecules = protein_mol_count[dendrite.protein]
            except KeyError: continue

            # For each receptive molecule:
            for mol_id,affinity in dendrite.protein.affinities.iteritems():
                try:
                    mol_concentration = mol_concentrations[mol_id]
                except KeyError: continue

                competing_proteins = mol_protein_count[mol_id]
                if competing_proteins == 0: continue


                # Proportion of molecule relative to competitors.
                mol_fraction = affinity * mol_concentration / competing_molecules

                # Proportion of protein relative to competitors.
                protein_count = affinity * dendrite.density
                protein_fraction = protein_count / competing_proteins

                # Calculate bound concentration.
                k = (1 - (mol_fraction * protein_fraction))
                bound = protein_count * (mol_concentration**2) / ( mol_concentration + k )

                # Transfer molecules.
                dendrite.bind(bound)

                if self.verbose:
                    print("Concentrations:")
                    print(" P: %f      M: %f" % (protein_count, mol_concentration))
                    print("Proportions::")
                    print("fP: %f    fM: %f" % (protein_fraction, mol_fraction))
                    print("Constant and final bound count:")
                    print("k: %f    bound: %f" % (k, bound))
                    print("")

    def complex_metabolize(self):
        """
        Stochastically metabolizes molecules in the pools according to the
            concentration of appropriate enzymes.
        Uses single molecule helper.
        """
        for mol in Molecules:
            self.metabolize_molecule(mol.mol_id,
                self.enzymes[mol.enzyme_id], mol.metab_rate)

    def metabolize_molecule(self, mol_id, enzyme_count, rate):
        """
        Metabolizes the given |mol| stochastically.
        """
        mol_count = self.get_concentration(mol_id)
        if mol_count <= 0.0: return
        elif mol_count < 0.0001: destroyed = mol_count
        else: 
            destroyed = metabolize(enzyme_count, mol_count, rate)
        self.remove_concentration(destroyed, mol_id)
        if self.verbose:
            print("Destroyed %f of mol %d" % (destroyed, mol_id))
            print("New concentrations: %f" % self.get_concentration(mol_id))
