import argparse

from plot import plot

from synapse import Synapse
from neuron_factory import NeuronFactory
from tools import PulseDriver

def external_current(rs=[-5, 2, 3, 5]):
    data = []
    for r in rs:
        neuron_factory = NeuronFactory()
        neuron = neuron_factory.create_neuron(probe=True)

        neuron_factory.register_driver(neuron,
            PulseDriver(current=r, period=1, length=1, delay=args.iterations/10))
        neuron_factory.step(args.iterations)

        data.append(("Current %f" % r, neuron.probe.data))
    if not args.silent:
        plot(data, title="External current")

def main():
    external_current()
    external_current(rs=[25])

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
    parser.add_argument("-i", "--iterations", type = int, default = 200, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
