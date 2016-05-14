import argparse
from plot import plot

from synapse import Synapse
from gap_junction import GapJunction
from neuron import Neuron

def pulse(strength1 = 0.0005, strength2 = 0.0):
    neuron1 = Neuron()
    neuron2 = Neuron()
    neuron3 = Neuron()

    Neuron.create_gap_junction(neuron1, neuron2, 1.0)

    for i in xrange(10000):
        neuron1.step(strength1)
        neuron2.step(strength2)
        neuron3.step(strength1)

    data = [neuron1.soma.get_data(name="G Neuron %f" % strength1),
        neuron2.soma.get_data(name="G Neuron %f" % strength2),
        neuron3.soma.get_data(name="Control Neuron %f" % strength1)]
    plot(data)

def main():
    pulse()

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
