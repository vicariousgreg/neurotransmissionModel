import argparse
from plot import plot

from neuron import Neuron
from neuron_factory import NeuronFactory
from tools import ConstantDriver

def test_gap_junction(strength1 = 0.0015, strength2 = 0.0):
    neuron_factory = NeuronFactory()
    neuron1 = neuron_factory.create_neuron(record=True)
    neuron2 = neuron_factory.create_neuron(record=True)
    neuron3 = neuron_factory.create_neuron(record=True)

    rest_time = 10
    driver1 = ConstantDriver(strength1, delay=rest_time)
    driver2 = ConstantDriver(strength2, delay=rest_time)
    driver3 = ConstantDriver(strength1, delay=rest_time)

    neuron_factory.register_driver(neuron1, driver1)
    neuron_factory.register_driver(neuron2, driver2)
    neuron_factory.register_driver(neuron3, driver3)

    neuron_factory.create_gap_junction(neuron1, neuron2, 0.5)

    neuron_factory.step(rest_time+args.iterations)

    data = [("Uncoupled", neuron3.get_record()),
            ("Coupled driven", neuron1.get_record()),
            ("Coupled undriven", neuron2.get_record())]
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
    parser.add_argument("-i", "--iterations", type = int, default = 100, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
