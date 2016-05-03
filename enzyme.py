# Enzyme model
#
# Enzymes metabolize molecules at a particular rate.

from enum import enum
from math import exp

def tanh(x):
    """
    Calculates tanh(x).

        2
    ----------   - 1
    1 + e^(-2x)

    """
    try: return (2.0 / (1.0 + exp(-2 * x))) - 1.0
    except OverflowError: return 0.0

def metabolize(enzyme_count, mol_count, rate):
    """
    Returns the number of molecules destroyed during metabolism.
    |enzyme_count| is the number of enzymes in the pool.
    |mol_count| is the number of molecules in the pool.
    |rate| is the metabolic rate.
    """
    try: return mol_count * tanh(rate*enzyme_count/mol_count)
    except ZeroDivisionError: return 0

# Enumeration of enzymes
Enzymes = enum(
    GLUTAMATE = 0,
    GABA = 1
)

num_enzymes=2
