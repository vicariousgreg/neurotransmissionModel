import argparse

from plot import plot

from synapse import Synapse
from axon import Axon
from dendrite import Dendrite
from simulation import run
from neural_network import NeuralNetwork

def synapse_metabolize(rs=[0.01, 0.1, 0.5, 1.0]):
    data = []

    for r in rs:
        nn = NeuralNetwork()
        syn = nn.create_synapse(enzyme_concentration=r)
        syn.set_concentration(1.0)

        axon_data,synapse_data,dendrite_data = run(nn, synapse=syn, iterations=100)
        data.append(("metabolize " + str(r), synapse_data))
    plot(data, title="Metabolize (enzyme concentration)")

def synapse_bind(rs=[0.01, 0.1, 0.5, 1.0]):
    data = []

    for r in rs:
        nn = NeuralNetwork()
        dendrite = nn.create_dendrite(release_rate=0, initial_size=r)
        syn = nn.create_synapse(enzyme_concentration=0.0)
        syn.set_concentration(1.0)

        axon_data,synapse_data,dendrite_data = run(nn, synapse=syn, dendrite=dendrite, iterations=50)
        data.append(("bind " + str(r), synapse_data))
    plot(data, title="Bind (dendrite density)")

def main():
    synapse_metabolize()
    synapse_bind()

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synapse->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
