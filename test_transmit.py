import argparse

from plot import plot

from synapse import Synapse
from neuron import Neuron
from soma import Soma
from neuron_factory import NeuronFactory, ActivationPulseDriver

def transmit(strength=0.25, delays=[None, 100]):
    data = []
    neuron_factory = NeuronFactory()
    if args.silent:
        pre_neuron = neuron_factory.create_neuron()
        for delay in delays:
            post_neuron = neuron_factory.create_neuron()
            synapse = neuron_factory.create_synapse(pre_neuron, post_neuron,
                axon_delay=delay)
    else:
        pre_neuron_name = "pre strength: %f" % strength
        pre_neuron = neuron_factory.create_neuron(probe_name=pre_neuron_name)

        post_neuron_names = []
        for delay in delays:
            name="post delay: %s" % str(delay)
            post_neuron_names.append(name)
            post_neuron = neuron_factory.create_neuron(probe_name=name)
            synapse = neuron_factory.create_synapse(pre_neuron, post_neuron,
                axon_delay=delay)

    neuron_factory.register_driver(pre_neuron,
        ActivationPulseDriver(activation=strength, period=500, length=1, decrement=0.01))
    neuron_factory.step(args.iterations)

    print("Saved %d out of %d cycles." % (neuron_factory.stable, neuron_factory.time))

    if not args.silent:
        data.append(neuron_factory.get_probe_data(pre_neuron_name))
        for name in post_neuron_names:
            data.append(neuron_factory.get_probe_data(name))
        plot(data, title="Synaptic transmission")

def main():
    #transmit(strength = 0.25)
    transmit(strength = 0.25, delays=[None])
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
    parser.add_argument("-i", "--iterations", type = int, default = 10000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
