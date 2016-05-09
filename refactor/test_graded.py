import argparse

from plot import plot

from simulation import run
from synapse import Synapse

def graded(rs=[1,5,10,25], spike_strengths=[0.1],
        print_axon=False, print_synaptic_cleft=False, print_dendrite=True):
    for r in rs:
        for s in spike_strengths:
            syn = Synapse(verbose=args.verbose)
            axon = syn.create_axon(release_time_factor=20,
                        replenish_rate=0.1,
                        reuptake_rate=0.5,
                        capacity=1.0,
                        verbose=args.verbose)
            dendrite = syn.create_dendrite(
                        density=1.0,
                        verbose=args.verbose)
            syn.set_enzyme_concentration(3.0)

            record_components = []
            if print_axon:
                record_components.append((
                    "release %s  rate: %s" % (str(r), str(s)), axon))
            if print_synaptic_cleft:
                record_components.append((
                    "synaptic cleft %s  rate: %s" % (str(r), str(s)),
                    syn.synaptic_cleft))
            if print_dendrite:
                record_components.append((
                    "dendrite %s  rate: %s" % (str(r), str(s)), dendrite))

            data = run(syn, record_components=record_components,
                iterations = args.iterations,
                frequency=r,
                increase=True,
                sustain=True,
                spike_strength=s)

            if not args.silent:
                plot(data, title="Graded potentials (firing rate)")

def main():
    graded(#rs=[10],
        print_axon=True,
        print_synaptic_cleft=True,
        print_dendrite=True)

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synaptic_cleft->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")
    parser.add_argument("-s", "--silent", action = "store_true", help = 
    """do not display graphs""")
    parser.add_argument("-i", "--iterations", type = int, default = 1000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
