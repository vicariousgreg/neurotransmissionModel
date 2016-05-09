# Membrane
#
# Membranes contain proteins at particular densities, and are also
#     Pool Clusters.  There are two types of membranes:
#
# Receptor membranes are primarily for Dendrites, and contain receptor
#     proteins.  These receptors can be occupied by any molecule with an
#     affinity for the particular type of receptor on the membrane.
#
# Transport membranes are primarily for axons, and reuptake one particular
#     endogenous molecule.  Some molecules, however, can block reuptake,
#     in which case the proteins behave more like receptors than transporters.
#     This blockage does not affect the axon, and only reduces the number of
#     transport proteins available for reuptake, thus lowering the rate of
#     reuptake.

from pool_cluster import PoolCluster

class Membrane(PoolCluster):
    def __init__(self, protein, density, environment=None):
        """
        Creates a membrane with a particular |density| of |protein|.
        This |protein| can be either a transporter or a receptor (see
            TransportMembrane and ReceptorMembrane sublcasses.
        The |environment| is passed through to the PoolCluster.
        Affinities for certain molecules are retreived from the protein.
        """
        self.protein = protein
        self.native_mol_id = protein.native_mol_id
        concentrations = dict([
            (mol_id, 0.0)
            for mol_id in protein.affinities])
        self.density = density
        self.affinities = protein.affinities
        PoolCluster.__init__(self, concentrations, environment)

    def get_available_proteins(self):
        """
        Gets the concentration of proteins available for activity.
        Because TransportMembranes and ReceptorMembranes behave differently,
            this method is to be overriden by these subclasses.
        """
        raise ValueError("Cannot simulate abstract class!")

    def get_native_concentration(self):
        """
        Gets the concentration of native molecule.
        """
        return self.get_concentration(self.native_mol_id)

    def get_foreign_concentration(self):
        """
        Gets the concentration of native molecule.
        """
        return sum(self.get_concentration(mol_id)
            for mol_id in self.affinities
            if mol_id != self.native_mol_id)

class ReceptorMembrane(Membrane):
    def __init__(self, receptor, density=1.0, environment=None):
        """
        Creates a receptor membrane with the given type of |receptor| protein.
            at the given |density|.
        """
        Membrane.__init__(self, receptor, density, environment)

    def get_available_proteins(self, mol_id):
        """
        The number of available proteins on the receptor membrane is the
            receptor density if the receptors are receptive to the given
            molecule.
        """
        return self.density if mol_id in self.affinities else 0.0

class TransporterMembrane(Membrane):
    def __init__(self, transporter, density=1.0, capacity=1.0, environment=None):
        """
        Creates a transporter membrane with the given type of |transporter|
            protein at the given |density|.
        The |capacity| indicates the membrane's capacity for its native
            molecule.
        """
        Membrane.__init__(self, transporter, density, environment)
        self.capacity = capacity
        self.set_concentration(capacity, transporter.native_mol_id)

    def get_available_proteins(self, mol_id):
        """
        The number of available proteins on the transporter membrane depends on
            the total density, the amount of molecules left to fill the
            memgrane capacity, and the number of receptors occupied by
            reuptake inhibitors.
        Concentration cannot exceed capacity, and the number of available
            proteins is limited to the number not occupied by reuptake
            inhibitors.  This, the amount available is the minimum of these
            two quantities.
        """
        if mol_id == self.native_mol_id:
            return min(self.density, self.capacity - self.get_native_concentration())
        elif mol_id in self.affinities:
            return self.density
        else:
            return 0.0
