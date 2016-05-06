import argparse

from plot import plot

from simulation import run
from synapse import Synapse

def graded(rs=[1,5,10, 15], spike_strengths=[0.25],
        print_axon=False, print_synaptic_cleft=False, print_dendrite=True):
    for r in rs:
        for s in spike_strengths:
            syn = Synapse(verbose=args.verbose)
            axon = syn.create_axon(release_time_factor=10,
                        replenish_rate=0.04,
                        reuptake_rate=0.01,
                        capacity=0.25,
                        verbose=args.verbose)
            dendrite = syn.create_dendrite(release_rate=0.05,
                        initial_size=0.5,
                        verbose=args.verbose)
            syn.set_enzyme_concentration(1.0)
            axon_data,synaptic_cleft_data,dendrite_data = run(syn,
                iterations = args.iterations,
                frequency=r,
                spike_strength=s,
                taper=True,
                verbose=args.verbose)

            data = []
            if print_axon:
                data.append(("axon %s  rate: %s" % (str(r), str(s)), axon_data))
            if print_synaptic_cleft:
                data.append(("synaptic_cleft %s  rate: %s" % (str(r), str(s)), synaptic_cleft_data))
            if print_dendrite:
                data.append(("dendrite %s  rate: %s" % (str(r), str(s)), dendrite_data))
            if not args.silent:
                plot(data, title="Graded Potentials (firing rate, initial strength)")
            #raw_input()

def main():
    graded(rs=[25, 50, 100],
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
    parser.add_argument("-i", "--iterations", type = int, default = 5000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
