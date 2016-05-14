import argparse

from plot import plot

from environment import NeuronEnvironment
from neuron_factory import NeuronFactory, CurrentPulseDriver


def pulse(strengths = [-2, -1, 5, 25]):
    data = []
    length = 7000
    period = 10000

    current_data = []
    current = -0.3

    for i in xrange(5000):
        current_data.append(-0.3)
    for i in xrange(5000, 35000):
        if i % period == 0:
            current = -0.2
        elif i % period == length:
            current = -0.3
        current_data.append(current)

    data.append(("current", current_data))

    for strength in strengths:
        neuron_factory = NeuronFactory()
        neuron = neuron_factory.create_neuron()

        neuron_factory.step(5000)
        neuron_factory.register_driver(neuron,
            CurrentPulseDriver(current=strength, period=period, length=length))
        neuron_factory.step(30000)

        data.append(neuron.soma.get_data("Pulse %f" % strength))
    if not args.silent:
        plot(data, title="Pulse")

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
