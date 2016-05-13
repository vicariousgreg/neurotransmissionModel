import argparse

from plot import plot

from simulation import run
from synapse import Synapse
from neuron import Neuron

def transmit(rs=[180, 160, 100], spike_strengths=[0.10],
        print_axon=False, print_synaptic_cleft=False, print_dendrite=True):
    data = []
    for r in rs:
        for s in spike_strengths:
            pre_neuron = Neuron()
            synapse = Synapse(verbose=args.verbose)
            axon = synapse.create_axon(
                        replenish_rate=0.1,
                        reuptake_rate=0.5,
                        capacity=1.0,
                        verbose=args.verbose)
            dendrite = synapse.create_dendrite(
                        density=0.05,
                        verbose=args.verbose)
            synapse.set_enzyme_concentration(1.0)
            post_neuron = Neuron()

            dendrite_data = []
            cleft_data = []

            rate = 500
            activation = 0.25
            for t in xrange(10000):
                if t % rate == 0:
                    pre_neuron.step(activation, resolution=100)
                    if activation > 0.0: activation -= 0.01
                else:
                    pre_neuron.step(0.0, resolution=100)

                if pre_neuron.v > -55.0:
                    axon.step(voltage = pre_neuron.v, resolution=100)
                else:
                    axon.step(resolution=100)

                synapse.step(t)
                post_neuron.step(0.05*dendrite.get_concentration(), resolution=100)
                dendrite_data.append(dendrite.get_concentration())
                cleft_data.append(synapse.synaptic_cleft.get_concentration())

            data.append(pre_neuron.get_data(name="pre time period: %d  strength: %f" % (r,s)))
            data.append(post_neuron.get_data(name="post time period: %d  strength: %f" % (r,s)))
            #data.append(axon.get_data())
            #data.append(("dendrite", dendrite_data))
            #data.append(("synaptic cleft", cleft_data))
    if not args.silent:
        plot(data, title="Spike train (firing rate)")

def main():
    transmit(
        rs=[500],
        #rs=[10000],
        spike_strengths=[0.3],
        #spike_strengths=[0.0],
        print_axon=True,
        print_synaptic_cleft=True,
        print_dendrite=True)

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
