import argparse

from plot import plot

from environment import NeuronEnvironment
from neuron_factory import NeuronFactory, CurrentPulseDriver


def pulse(strengths = [-2, -1, 5, 25]):
    data = []
    length = 7000
    period = 10000
    rest_length = 1000

    for strength in strengths:
        neuron_factory = NeuronFactory()
        neuron_name = "Pulse %f" % strength
        neuron = neuron_factory.create_neuron(probe_name=neuron_name)

        driver_name = "Strength %f" % strength
        neuron_factory.register_driver(neuron,
            CurrentPulseDriver(current=strength, period=period, length=length, delay=rest_length, record=True),
            name = driver_name)
        neuron_factory.step(rest_length+args.iterations)

        data.append(neuron_factory.get_probe_data(neuron_name))
    data.append(neuron_factory.get_driver_data(driver_name))
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
    parser.add_argument("-i", "--iterations", type = int, default = 39000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
