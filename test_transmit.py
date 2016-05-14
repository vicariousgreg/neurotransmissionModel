import argparse

from plot import plot

from synapse import Synapse
from neuron import Neuron
from soma import Soma
from neuron_factory import NeuronFactory, ActivationPulseDriver

def transmit(strength=0.3, delays=[None, 100]):
    data = []
    neuron_factory = NeuronFactory()
    pre_neuron_name = "pre strength: %f" % strength
    pre_neuron = neuron_factory.create_neuron(probe_name=pre_neuron_name)

    post_neuron_names = []
    for delay in delays:
        name="post delay: %s" % str(delay)
        post_neuron_names.append(name)
        post_neuron = neuron_factory.create_neuron(probe_name=name)
        synapse = neuron_factory.create_synapse(pre_neuron, post_neuron, axon_delay=delay)
        #axon = pre_neuron.axons[0]
        #dendrite = post_neuron.dendrites[0]

    #dendrite_data = []
    #cleft_data = []

    neuron_factory.register_driver(pre_neuron,
        ActivationPulseDriver(activation=strength, period=500, length=1, decrement=0.01))
    for t in xrange(10000):
        neuron_factory.step()
        #dendrite_data.append(dendrite.get_concentration())
        #cleft_data.append(synapse.synaptic_cleft.get_concentration())

    data.append(neuron_factory.get_probe_data(pre_neuron_name))
    for name in post_neuron_names:
        data.append(neuron_factory.get_probe_data(name))
    #data.append(axon.get_data())
    #data.append(("dendrite", dendrite_data))
    #data.append(("synaptic cleft", cleft_data))
    if not args.silent:
        plot(data, title="Synaptic transmission")

def main():
    transmit(strength = 0.3)

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
