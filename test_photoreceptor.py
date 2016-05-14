import argparse

from plot import plot

from simulation import run
from synapse import Synapse
from soma import Soma
from photoreceptor import Photoreceptor

def transmit(
        #spike_strengths=[0.0]):
        spike_strengths=[0.1, 0.5]):
    data = []
    period = 5000
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

    for strength in spike_strengths:
        soma = Photoreceptor()
        synapse = Synapse(verbose=args.verbose)
        axon = synapse.create_axon(
                    replenish_rate=0.1,
                    reuptake_rate=0.5,
                    capacity=1.0,
                    verbose=args.verbose)

        m=0.0
        for i in xrange(5000):
            soma.step(m, resolution=100)
        for i in xrange(30000):
            if i % frequency == 0:
                m = strength
            elif i % frequency == period:
                m = 0.0
            soma.step(m, resolution=100)

        data.append(soma.get_data("Pulse %f" % strength))
        data.append(axon.get_data())
    if not args.silent:
        plot(data, title="Photoreceptor test")

def main():
    transmit()

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
