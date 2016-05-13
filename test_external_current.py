import argparse

from plot import plot

from simulation import run
from synapse import Synapse
from neuron import Neuron

def external_current(rs=[-2, -1, 0, 1, 5, 10]):
    data = []
    for r in rs:
        neuron = Neuron()

        for i in xrange(1000):
            neuron.step(0.0, resolution=100)

        neuron.iapp = r
        for i in xrange(10000):
            neuron.step(0.0, resolution=100)

        data.append(neuron.get_data(name="current: %f" % r))
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
