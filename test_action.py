import argparse

from plot import plot

from simulation import run
from synapse import Synapse
from neuron import Neuron

def action(rs=[363, 300, 100], spike_strengths=[0.043],
        print_axon=False, print_synaptic_cleft=False, print_dendrite=True):
    data = []
    for r in rs:
        for s in spike_strengths:
            syn = Synapse(verbose=args.verbose)
            axon = syn.create_axon(release_time_factor=100,
                        replenish_rate=0.1,
                        reuptake_rate=0.5,
                        capacity=1.0,
                        verbose=args.verbose)
            dendrite = syn.create_dendrite(
                        density=1.0,
                        verbose=args.verbose)
            syn.set_enzyme_concentration(0.1)

            neuron = Neuron()

            record_components = [(
                "dendrite %s  rate: %s" % (str(r), str(s)), dendrite)]

            dendrite_data = run(syn, record_components=record_components,
                iterations = args.iterations,
                frequency=r,
                #increase=True,
                #sustain=True,
                sample_rate=1,
                spike_strength=s)

            for i in dendrite_data[0][1]:
                neuron.step(i, resolution=100)

            data.append(neuron.get_data(name="freq: %d  strength: %f" % (r,s)))
    plot(data, title="Graded potentials (firing rate)")

def main():
    action(#rs=[10],
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
    parser.add_argument("-i", "--iterations", type = int, default = 2500, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
