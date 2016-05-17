import argparse

from plot import plot

from synapse import Synapse
from neuron_factory import NeuronFactory, CurrentPulseDriver

def external_current(rs=[-2, -1, 0, 1, 5, 10]):
    data = []
    for r in rs:
        neuron_factory = NeuronFactory()
        neuron_name = "current: %f" % r
        neuron = neuron_factory.create_neuron(probe_name=neuron_name)

        neuron_factory.register_driver(neuron,
            CurrentPulseDriver(current=r, period=1, length=1, delay=args.iterations/10))
        neuron_factory.step(args.iterations/10)
        neuron_factory.step(args.iterations)

        data.append(neuron_factory.get_probe_data(neuron_name))
    if not args.silent:
        plot(data, title="External current")

def main():
    external_current()

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
