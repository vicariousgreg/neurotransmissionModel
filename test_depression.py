import argparse

from plot import plot

from axon import Axon
from dendrite import Dendrite
from synaptic_cleft import SynapticCleft
from simulation import run
from neural_network import NeuralNetwork

def depression(rs=[1,5,10, 15], spike_strengths=[0.25],
        print_axon=False, print_synaptic_cleft=False, print_dendrite=True):
    for r in rs:
        for s in spike_strengths:
            nn = NeuralNetwork()
            axon = nn.create_axon(release_time_factor=10,
                        replenish_rate=0.05,
                        reuptake_rate=0.05,
                        capacity=0.25,
                        verbose=args.verbose)
            dendrite = nn.create_dendrite(release_rate=0.25,
                        initial_size=0.25,
                        verbose=args.verbose)
            synaptic_cleft = nn.create_synaptic_cleft(enzyme_concentration=0.25, verbose=args.verbose)
            axon_data,synaptic_cleft_data,dendrite_data = run(nn,
                axon=axon,
                synaptic_cleft=synaptic_cleft,
                dendrite=dendrite,
                iterations = args.iterations,
                frequency=r,
                spike_strength=s,
                verbose=args.verbose)

            data = []
            if print_axon:
                data.append(("axon %s  rate: %s" % (str(r), str(s)), axon_data))
            if print_synaptic_cleft:
                data.append(("synaptic_cleft %s  rate: %s" % (str(r), str(s)), synaptic_cleft_data))
            if print_dendrite:
                data.append(("dendrite %s  rate: %s" % (str(r), str(s)), dendrite_data))
            plot(data, title="Short Term Depression (firing rate, strength)")
            #raw_input()

def main():
    depression(rs=[25, 50, 100],
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
    parser.add_argument("-i", "--iterations", type = int, default = 500, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
