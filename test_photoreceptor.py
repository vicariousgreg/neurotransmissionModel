import argparse

from plot import plot

from neuron import NeuronTypes
from neuron_factory import NeuronFactory, ActivationPulseDriver

def test_photoreceptor(
        spike_strengths=[0.5]):
        #spike_strengths=[0.1, 0.5, 0.7]):
    data = []
    length = 7000
    period = 12000

    current_data = []
    for i in xrange(5000):
        current_data.append(-0.5)
    for i in xrange(5000, 35000):
        if i % period < length:
            current_data.append(-0.4)
        else:
            current_data.append(-0.5)

    data.append(("current", current_data))

    for strength in spike_strengths:
        neuron_factory = NeuronFactory()
        pre_neuron_name = "Photoreceptor %f" % strength
        post_neuron_name = "Postsynaptic %f" % strength

        photoreceptor = neuron_factory.create_neuron(
            neuron_type=NeuronTypes.PHOTORECEPTOR,
            probe_name = pre_neuron_name)
        post = neuron_factory.create_neuron(probe_name=post_neuron_name)

        axon_name="axon %f" % strength
        cleft_name="synaptic cleft %f" % strength
        dendrite_name="dendrite %f" % strength
        synapse = neuron_factory.create_synapse(photoreceptor, post, dendrite_strength=0.0125,
            axon_probe_name=axon_name, cleft_probe_name=cleft_name, dendrite_probe_name=dendrite_name)
        synapse.set_enzyme_concentration(0.5)

        cleft_data = []
        dendrite_data = []

        neuron_factory.step(5000)
        neuron_factory.register_driver(photoreceptor,
            ActivationPulseDriver(activation=strength, period=period, length=length))
        neuron_factory.step(args.iterations)

        data.append(neuron_factory.get_probe_data(pre_neuron_name))
        data.append(neuron_factory.get_probe_data(post_neuron_name))
        #data.append(neuron_factory.get_probe_data(axon_name))
        #data.append(neuron_factory.get_probe_data(cleft_name))
        data.append(neuron_factory.get_probe_data(dendrite_name))
    if not args.silent:
        plot(data, title="Photoreceptor test")

def main():
    test_photoreceptor()

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
    parser.add_argument("-i", "--iterations", type = int, default = 30000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
