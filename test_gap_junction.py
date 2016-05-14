import argparse
from plot import plot

from synapse import Synapse
from neuron import Neuron
from environment import NeuronEnvironment
from neuron_factory import NeuronFactory, ConstantDriver

def test_gap_junction(strength1 = 0.00065, strength2 = 0.0):
    neuron_factory = NeuronFactory()
    neuron1_name = "G Neuron %f" % strength1
    neuron1 = neuron_factory.create_neuron(probe_name=neuron1_name)

    neuron2_name = "G Neuron %f" % strength2
    neuron2 = neuron_factory.create_neuron(probe_name=neuron2_name)

    neuron3_name = "Control Neuron %f" % strength1
    neuron3 = neuron_factory.create_neuron(probe_name=neuron3_name)

    driver1 = ConstantDriver(strength1)
    driver2 = ConstantDriver(strength2)

    neuron_factory.register_driver(neuron1, driver1)
    neuron_factory.register_driver(neuron2, driver2)
    neuron_factory.register_driver(neuron3, driver1)

    neuron_factory.create_gap_junction(neuron1, neuron2, 1.0)

    neuron_factory.step(10000)

    data = [neuron_factory.get_probe_data(neuron1_name),
        neuron_factory.get_probe_data(neuron2_name),
        neuron_factory.get_probe_data(neuron3_name)]
    if not args.silent:
        plot(data, title="Gap junction test")

def main():
    test_gap_junction()

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synaptic_cleft->dendrite.""")
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
