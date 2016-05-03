# Enumeration for molecules.
#
# NEUROTRANSMITTERS:
#     Gluatamate: excitatory
#     GABA: inhibitory

from enum import enum
from enzyme import Enzymes

Molecules = enum(
    GLUTAMATE = 0,
    GABA = 1
)

num_molecules=2

# List of (enzyme, rate) for each molecule
Metabolizers = [
    (Enzymes.GLUTAMATE,1),
    (Enzymes.GABA,1)
]
