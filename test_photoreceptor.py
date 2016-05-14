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
        neuron = neuron_factory.create_neuron(
            neuron_type=NeuronTypes.PHOTORECEPTOR)
        post = neuron_factory.create_neuron()
        synapse = neuron_factory.create_synapse(neuron, post, dendrite_strength=0.015)
        axon = neuron.axons[0]
        dendrite = post.dendrites[0]
        synapse.set_enzyme_concentration(0.5)

        cleft_data = []
        dendrite_data = []

        for i in xrange(5000):
            neuron_factory.step()
            cleft_data.append(synapse.synaptic_cleft.get_concentration())
            dendrite_data.append(dendrite.get_concentration())
        neuron_factory.register_driver(neuron,
            ActivationPulseDriver(activation=strength, period=period, length=length))
        for i in xrange(30000):
            neuron_factory.step()
            cleft_data.append(synapse.synaptic_cleft.get_concentration())
            dendrite_data.append(dendrite.get_concentration())

        data.append(neuron.soma.get_data("Photoreceptor %f" % strength))
        data.append(post.soma.get_data("Postsynaptic %f" % strength))
        #data.append(axon.get_data())
        data.append(("dendrite %f" % strength, dendrite_data))
        #data.append(("synaptic cleft", cleft_data))
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

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
