import argparse

from plot import plot

from neuron import Neuron
from soma import Soma
from neuron_factory import NeuronFactory
from tools import PulseDriver

def transmit(strength=0.25, delays=[None, 100]):
    data = []
    neuron_factory = NeuronFactory()
    dendrite_strength = 1
    if args.silent:
        pre_neuron = neuron_factory.create_neuron()
        for delay in delays:
            post_neuron = neuron_factory.create_neuron()
            synapse = neuron_factory.create_synapse(pre_neuron, post_neuron,
                axon_delay=delay, dendrite_strength=dendrite_strength)
    else:
        pre_neuron = neuron_factory.create_neuron(record=True)

        post_neurons = []
        for delay in delays:
            post_neuron = neuron_factory.create_neuron(record=True)
            post_neurons.append(post_neuron)
            synapse = neuron_factory.create_synapse(pre_neuron, post_neuron,
                axon_delay=delay, dendrite_strength=dendrite_strength)

    neuron_factory.register_driver(pre_neuron,
        PulseDriver(current=strength, period=100, length=1, delay=25))
    neuron_factory.step(args.iterations)

    #print("Saved %d out of %d cycles." % (neuron_factory.stable_count, neuron_factory.time))

    if not args.silent:
        data.append(("Pre neuron", pre_neuron.get_record()))
        for post_neuron in post_neurons:
            data.append(("Post neuron", post_neuron.get_record()))
        plot(data, title="Synaptic transmission")

def main():
    #transmit(strength = -0.5)
    transmit(strength = 100, delays=[10])
    #transmit(strength = 0.1, delays=[None])

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
