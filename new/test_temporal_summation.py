import argparse

from plot import plot

from neuron import NeuronTypes
from neuron_factory import NeuronFactory
from tools import PulseDriver

def temporal_summation(num_pre = 3):
    data = []

    neuron_factory = NeuronFactory()
    post_neuron = neuron_factory.create_neuron(probe=True)

    pre_neurons = []
    for i in xrange(num_pre):

        pre_neuron = neuron_factory.create_neuron(
            neuron_type=NeuronTypes.GANGLION,
            probe = True)
        pre_neurons.append(pre_neuron)

        synapse = neuron_factory.create_synapse(pre_neuron, post_neuron,
            dendrite_strength=25, axon_delay=5)
        synapse.set_enzyme_concentration(0.5)

        neuron_factory.register_driver(pre_neuron,
            PulseDriver(current=100, period=100*(i+1),
                length=1, delay=10 + (2*i), record=True))

    neuron_factory.step(args.iterations)

    #print("Saved %d out of %d cycles." % (neuron_factory.stable_count, neuron_factory.time))

    for pre_neuron in pre_neurons:
        data.append(("Pre", pre_neuron.probe.data))
    data.append(("Post", post_neuron.probe.data))
    if not args.silent:
        plot(data, title="Temporal summation test")

def main():
    temporal_summation()

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
    parser.add_argument("-i", "--iterations", type = int, default = 1000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
