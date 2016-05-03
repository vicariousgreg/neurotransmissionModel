# Enzyme model
#
# Enzymes metabolize molecules at a particular rate.

from enum import enum
from math import exp

def metabolize(self, num_enzymes, mol_count, rate):
    """
    Returns the number of molecules destroyed during metabolism.
    |num_enzymes| is the number of enzymes in the pool.
    |mol_count| is the number of molecules in the pool.
    |rate| is the metabolic rate.
    """
    return mol_count * -exp(mol_count)

# Enumeration of enzymes
Enzymes = enum(
    GLUTAMATE = 0,
    GABA = 1
)
