import argparse
from plot import plot
from synapse import Synapse
from molecule import Molecule_IDs

def run(synapse, record_components = [], molecule = Molecule_IDs.GLUTAMATE,
        iterations=100, sample_rate=1, verbose=False):
    data = [(name,[]) for name,component in record_components]

    def record(time):
        for i,component in enumerate(record_components):
            data[i][1].append(component[1].get_concentration(molecule))

        if verbose:
                ",".join("%-20s" % str(x[-1]) for x in data)

    for t in xrange(iterations):
        synapse.step(t)
        if t % sample_rate == 0: record(t)

    return data

def main():
    print_axon=True
    print_synaptic_cleft=True
    print_dendrite=True

    syn = Synapse(verbose=args.verbose)
    axon = syn.create_axon(
                replenish_rate=0.1,
                reuptake_rate=0.5,
                capacity=0.5,
                verbose=args.verbose)
    dendrite = syn.create_dendrite(
                density=1.0,
                verbose=args.verbose)
    syn.set_enzyme_concentration(1.0)

    record_components = []
    if print_axon:
        record_components.append((
            "axon", axon))
    if print_synaptic_cleft:
        record_components.append((
            "synaptic cleft", syn.synaptic_cleft))
    if print_dendrite:
        record_components.append((
            "dendrite", dendrite))

    data = run(syn, record_components=record_components,
        iterations = 100)

    if not args.silent:
        plot(data, title="Simple spike release")

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synaptic cleft->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")
    parser.add_argument("-s", "--silent", action = "store_true", help = 
    """do not display graphs""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
