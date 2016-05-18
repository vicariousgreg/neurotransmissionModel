import argparse

from plot import plot

from neuron import NeuronTypes
from neuron_factory import NeuronFactory, ActivationPulseDriver

def temporal_summation(num_pre = 3):
    data = []

    neuron_factory = NeuronFactory()
    post_neuron_name = "Postsynaptic"
    post_neuron = neuron_factory.create_neuron(probe_name=post_neuron_name)

    pre_neuron_names = []
    for i in xrange(num_pre):
        pre_neuron_name = "Presynaptic %d" % i
        pre_neuron_names.append(pre_neuron_name)

        pre_neuron = neuron_factory.create_neuron(
            neuron_type=NeuronTypes.GANGLION,
            probe_name = pre_neuron_name)

        synapse = neuron_factory.create_synapse(pre_neuron, post_neuron,
            dendrite_strength=0.0015, axon_delay=500)
        synapse.set_enzyme_concentration(0.5)

        neuron_factory.register_driver(pre_neuron,
            ActivationPulseDriver(activation=0.5, period=5000*(i+1),
                length=1, delay=1000 + (100*i), record=True))

    neuron_factory.step(args.iterations)

    print("Saved %d out of %d cycles." % (neuron_factory.stable_count, neuron_factory.time))

    for pre_neuron_name in pre_neuron_names:
        data.append(neuron_factory.get_probe_data(pre_neuron_name))
    data.append(neuron_factory.get_probe_data(post_neuron_name))
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
    parser.add_argument("-i", "--iterations", type = int, default = 50000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
