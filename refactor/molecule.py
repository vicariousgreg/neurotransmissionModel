# Enumeration for molecules.
#
# NEUROTRANSMITTERS:
#     Gluatamate: excitatory
#     GABA: inhibitory

from enum import enum
from math import exp

#################
"""  ENZYMES  """
#################

Enzymes = enum(
    GLUTAMATE = 0,
    GABA      = 1
)


#################
""" MOLECULES """
#################

class Molecule:
    def __init__(self, name, mol_id, enzyme_id, metab_rate):
        """
        Molecules have a |name|, a unique identifier, a corresponding enzyme,
            and a rate of metabolism by that enzyme.
        """
        self.name = name
        self.mol_id = mol_id
        self.enzyme_id = enzyme_id
        self.metab_rate = metab_rate

Molecules = [
    Molecule("Glutamate", mol_id=0, enzyme_id=0, metab_rate=0.25),
    Molecule("GABA", mol_id=1, enzyme_id=1, metab_rate=0.25)
]

Molecule_IDs = enum(
    GLUTAMATE = 0,
    GABA = 1
)


#################
""" RECEPTORS """
#################

class Receptor:
    def __init__(self, native_mol_id, native_affinity, voltage_dependent=False):
        """
        Receptors have a native molecule specified by |native_mol_id|,
            foreign agonists, and foreign antagonists.  Any molecule that
            interacts with the receptor has an affinity.
        A receptor can be optionally voltage dependent, which does not affect
            neurotransmission, but affects how the receptor modifies the host
            cell.
        """
        self.native_mol_id = native_mol_id
        self.voltage_dependent = voltage_dependent
        self.agonists = [native_mol_id]
        self.antagonists = []
        self.affinities = dict([(native_mol_id, native_affinity)])

    def add_agonist(self, mol_id, affinity):
        self.agonists.append(mol_id)
        self.affinities[mol_id] = affinity

    def add_antagonist(self, mol_id, affinity):
        self.antagonists.append(mol_id)
        self.affinities[mol_id] = affinity

Receptors = enum(
    AMPA = Receptor(Molecule_IDs.GLUTAMATE, 0.8),
    NMDA = Receptor(Molecule_IDs.GLUTAMATE, 0.4, voltage_dependent=True),
    GABA = Receptor(Molecule_IDs.GABA, 0.9)
)


####################
""" TRANSPORTERS """
####################

class Transporter:
    def __init__(self, native_mol_id):
        """
        Transporters have a native molecule that they transport, but can be
            blocked by foreign molecules (reuptake inhibitors).  As with
            receptors, every molecule that interacts with the protein has a
            particular affinity for binding to it.  The native molecule has
            a full affinity, and does not get bound (see TransporterMembrane).
        """
        self.native_mol_id = native_mol_id
        self.reuptake_inhibitors = []
        self.affinities = dict([(native_mol_id, 1.0)])

    def add_reuptake_inhibitor(self, mol_id, affinity):
        self.reuptake_inhibitors.append(mol_id)
        self.affinities[mol_id] = affinity

Transporters = enum(
    GLUTAMATE = Transporter(Molecule_IDs.GLUTAMATE),
    GABA = Transporter(Molecule_IDs.GABA)
)


##################
""" METABOLISM """
##################

def tanh(x):
    """
    Calculates tanh(x).

        2
    ----------   - 1
    1 + e^(-2x)

    """
    try: return (2.0 / (1.0 + exp(-2 * x))) - 1.0
    except OverflowError: return 0.0

def metabolize_beta(enzyme_count, mol_count, rate, environment):
    """
    Returns the number of molecules destroyed during metabolism.
    |enzyme_count| is the number of enzymes in the pool.
    |mol_count| is the number of molecules in the pool.
    |rate| is the metabolic rate.
    The |environment| provides the stochastic method for metablism.
    """
    baseline = (mol_count * enzyme_count) * tanh(rate*(1+(enzyme_count*mol_count)))
    destroyed = environment.beta(baseline, rate=10)
    return destroyed

"""
Enzyme degredation
V_0 = V_max * [S] / ( [S] + K_M )

where V_0 is the initial "velocity" of the reaction
so that's basically up to your choice of units
molecules per time
whatever
V_max is the maximum velocity of the enzyme
that you'll have to look up
[S] is the substrate concentration
and K_M is the michaelis menten constant
also a constant you look up for the individual enzyme
so then you generally assume the reaction is always at V_0
and that's your d/dt [L]
and you have a little system of DEs
"""
def metabolize(enzyme_count, mol_count, rate, environment):
    # Determine V_MAX based on enzyme concentration
    V_max = enzyme_count

    # Determine K_M
    K_M = 1.0 - rate

    # Scale?
    scale = 100
    mol_count *= scale
    enzyme_count *= scale
    K_M *= scale

    # Caclulate rate of change
    V_0 = V_max * mol_count / ( mol_count + K_M )

    # Multiply by metabolic rate
    return V_0 / scale
