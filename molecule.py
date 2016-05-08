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

Molecules = enum(
    GLUTAMATE = 0,
    GABA      = 1
)

# Maps molecules to native molecules.
# Molecule: index
# (Analog, metabolic rate, affinity)
Analogs = [
    (Molecules.GLUTAMATE, 1.0, 0.9),
    (Molecules.GABA,      1.0, 0.9)
]


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

def metabolize(enzyme_count, mol_count, rate, environment):
    """
    Returns the number of molecules destroyed during metabolism.
    |enzyme_count| is the number of enzymes in the pool.
    |mol_count| is the number of molecules in the pool.
    |rate| is the metabolic rate.
    """
    baseline = (mol_count * enzyme_count) * tanh(rate*(1+(enzyme_count*mol_count)))
    destroyed = environment.beta(baseline, rate=10)
    return destroyed
