def epsp(strength, activation, neuron):
    curr = activation*strength
    if curr > 0.0:
        #print("epsp", curr)
        neuron.change_ligand_current(curr)

def voltage_epsp(strength, activation, neuron):
    if neuron.soma.get_voltage() > -60.0:
        neuron.change_ligand_current(strength*activation)

def ipsp(strength, activation, neuron):
    neuron.change_ligand_current(-strength*activation)
