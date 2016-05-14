import argparse

from plot import plot

from synapse import Synapse
from neuron import Neuron
from soma import Soma
from environment import NeuronEnvironment

def transmit(spike_strengths=[0.10],
        print_axon=False, print_synaptic_cleft=False, print_dendrite=True):
    data = []
    for s in spike_strengths:
        environment = NeuronEnvironment()
        pre_neuron = Neuron(environment=environment)
        post_neuron = Neuron(environment=environment)
        synapse = Neuron.create_synapse(pre_neuron, post_neuron)
        axon = pre_neuron.axons[0]
        dendrite = post_neuron.dendrites[0]

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
            synapse.step(t)
            post_neuron.step(0.05*dendrite.get_concentration(), resolution=100)
            environment.step()

            dendrite_data.append(dendrite.get_concentration())
            cleft_data.append(synapse.synaptic_cleft.get_concentration())

        data.append(pre_neuron.soma.get_data(name="pre strength: %f" % s))
        data.append(post_neuron.soma.get_data(name="post strength: %f" % s))
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
