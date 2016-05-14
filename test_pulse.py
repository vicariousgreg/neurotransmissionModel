import argparse

from plot import plot

from soma import Soma
from environment import NeuronEnvironment


def pulse(strengths = [-2, -1, 5, 25]):
    data = []
    period = 7000
    frequency = 10000

    current_data = []
    current = 0.0

    for i in xrange(5000):
        current_data.append(-0.3)
    for i in xrange(30000):
        if i % frequency == 0:
            current = -0.2
        elif i % frequency == period:
            current = -0.3
        current_data.append(current)

    data.append(("current", current_data))

    for strength in strengths:
        environment = NeuronEnvironment()
        soma = Soma(environment=environment)

        for i in xrange(5000):
            soma.step(0.0, resolution=100)
            environment.step()
        for i in xrange(30000):
            if i % frequency == 0:
                soma.iapp = strength
            elif i % frequency == period:
                soma.iapp = 0.0
            soma.step(0.0, resolution=100)
            environment.step()

        data.append(soma.get_data("Pulse %f" % strength))
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
