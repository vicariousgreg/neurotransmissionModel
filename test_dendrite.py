import argparse

from plot import plot

from molecule import Molecules
from synapse import Synapse
from dendrite import Dendrite

def run_simulation(dendrite, syn=None, iterations=100, verbose=False):
    if syn is None:
        syn = Synapse(0.0)
        syn.set_concentration(1.0)
    syn.connect(dendrite)
    synapse_data = []
    dendrite_data = []

    def record(time):
        synapse_data.append(syn.get_concentration(Molecules.GLUTAMATE))
        dendrite_data.append(dendrite.get_concentration())

        if args.verbose:
            output = (time,syn.get_concentration(), dendrite.get_concentration())
            print(",".join("%-20s" % str(x) for x in output))

    for t in xrange(iterations):
        record(t)
        syn.step(t)
        dendrite.step(t)
    record(t)

    return synapse_data, dendrite_data

def dendrite_bind(rs=[0.1, 0.5, 1.0], print_synapse=False):
    data = []
    dendrite = Dendrite(release_rate=0, initial_size=1.0, verbose=True)
    for r in rs:
        syn = Synapse(0.0)
        syn.set_concentration(r)

        synapse_data, dendrite_data = run_simulation(dendrite, syn=syn, iterations=100)
        data.append(("bind " + str(r), dendrite_data))
        if print_synapse: data.append(("synapse " + str(r), synapse_data))
    plot(data, title="Bind (synapse concentration)")

def dendrite_release(rs=[0.1, 1, 10, 100], print_synapse=False):
    data = []
    for r in rs:
        dendrite = Dendrite(release_rate=r, initial_size=1.0, verbose=True)
        dendrite.set_concentration(1.0)
        syn = Synapse(0.0)

        synapse_data, dendrite_data = run_simulation(dendrite, syn=syn, iterations=100)
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
