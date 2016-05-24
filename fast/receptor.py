from enum import enum

class Receptor:
    def __init__(self, activation_function):
        self.activation_function = activation_function

    def add_agonist(self, mol_id, affinity):
        self.agonists.append(mol_id)
        self.affinities[mol_id] = affinity

    def add_antagonist(self, mol_id, affinity):
        self.antagonists.append(mol_id)
        self.affinities[mol_id] = affinity

def epsp(strength, activation, neuron):
    curr = activation*strength
    if curr > 0.0:
        neuron.change_ligand_current(curr)

def voltage_epsp(strength, activation, neuron):
    if neuron.soma.get_voltage() > -60.0:
        neuron.change_ligand_current(strength*activation)

def ipsp(strength, activation, neuron):
    neuron.change_ligand_current(-strength*activation)

Receptors = enum(
    AMPA = Receptor(epsp),
    NMDA = Receptor(voltage_epsp),
    GABA = Receptor(ipsp)
)
