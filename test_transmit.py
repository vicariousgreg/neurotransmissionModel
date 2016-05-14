import argparse

from plot import plot

from synapse import Synapse
from soma import Soma

def transmit(spike_strengths=[0.10],
        print_axon=False, print_synaptic_cleft=False, print_dendrite=True):
    data = []
    for s in spike_strengths:
        pre_soma = Soma()
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
        post_soma = Soma()

        dendrite_data = []
        cleft_data = []

        rate = 500
        activation = 0.25
        for t in xrange(10000):
            if t % rate == 0:
                pre_soma.step(activation, resolution=100)
                if activation > 0.0: activation -= 0.01
            else:
                pre_soma.step(0.0, resolution=100)

            if pre_soma.v > -55.0:
                axon.step(voltage = pre_soma.v, resolution=100)
            else:
                axon.step(resolution=100)

            synapse.step(t)
            post_soma.step(0.05*dendrite.get_concentration(), resolution=100)

            dendrite_data.append(dendrite.get_concentration())
            cleft_data.append(synapse.synaptic_cleft.get_concentration())

        data.append(pre_soma.get_data(name="pre strength: %f" % s))
        data.append(post_soma.get_data(name="post strength: %f" % s))
        #data.append(axon.get_data())
        #data.append(("dendrite", dendrite_data))
        #data.append(("synaptic cleft", cleft_data))
    if not args.silent:
        plot(data, title="Spike train (firing rate)")

def main():
    transmit(
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
