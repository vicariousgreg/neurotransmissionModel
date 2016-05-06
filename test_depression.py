import argparse

from plot import plot

from axon import Axon
from dendrite import Dendrite
from synapse import Synapse
from simulation import run

def depression(rs=[1,5,10, 15], spike_strengths=[0.25],
        print_axon=False, print_synapse=False, print_dendrite=True):
    for r in rs:
        for s in spike_strengths:
            axon = Axon(release_time_factor=10,
                        replenish_rate=0.05,
                        reuptake_rate=0.05,
                        capacity=0.25,
                        verbose=args.verbose)
            dendrite = Dendrite(release_rate=0.25,
                        initial_size=0.25,
                        verbose=args.verbose)
            synapse = Synapse(0.25, verbose=args.verbose)
            axon_data,synapse_data,dendrite_data = run(
                axon=axon,
                synapse=synapse,
                dendrite=dendrite,
                iterations = args.iterations,
                frequency=r,
                spike_strength=s,
                verbose=args.verbose)

            data = []
            if print_axon:
                data.append(("axon %s  rate: %s" % (str(r), str(s)), axon_data))
            if print_synapse:
                data.append(("synapse %s  rate: %s" % (str(r), str(s)), synapse_data))
            if print_dendrite:
                data.append(("dendrite %s  rate: %s" % (str(r), str(s)), dendrite_data))
            plot(data, title="Short Term Depression (firing rate, strength)")
            #raw_input()

def main():
    depression(rs=[25, 50, 100],
        print_axon=True,
        print_synapse=True,
        print_dendrite=True)

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synapse->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")
    parser.add_argument("-i", "--iterations", type = int, default = 500, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
