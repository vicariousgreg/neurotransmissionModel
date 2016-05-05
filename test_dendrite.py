import argparse

from plot import plot

from synapse import Synapse
from dendrite import Dendrite
from simulation import run

def dendrite_bind(rs=[0.1, 0.5, 1.0], print_synapse=False):
    data = []
    dendrite = Dendrite(release_rate=0, initial_size=1.0, verbose=args.verbose)
    for r in rs:
        syn = Synapse(0.0)
        syn.set_concentration(r)

        axon_data,synapse_data, dendrite_data = run(dendrite=dendrite, synapse=syn, iterations=100, verbose=args.verbose)
        data.append(("bind " + str(r), dendrite_data))
        if print_synapse: data.append(("synapse " + str(r), synapse_data))
    plot(data, title="Bind (synapse concentration)")

def dendrite_release(rs=[0.1, 0.5, 1, 5], print_synapse=False):
    data = []
    for r in rs:
        dendrite = Dendrite(release_rate=r, initial_size=1.0, verbose=args.verbose)
        dendrite.set_concentration(1.0)

        axon_data,synapse_data, dendrite_data = run(dendrite=dendrite, iterations=25, verbose=args.verbose)
        data.append(("release " + str(r), dendrite_data))
        if print_synapse: data.append(("synapse " + str(r), synapse_data))
    plot(data, title="Release (release rate)")

def main():
    dendrite_bind(print_synapse=False)
    dendrite_release()

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
