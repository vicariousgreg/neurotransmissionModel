import argparse

from plot import plot

from axon import Axon
from synapse import Synapse
from simulation import run
from neural_network import NeuralNetwork

def axon_release(rs=[1,5,10, 100, 1000], spike_strengths=[1.0], print_synapse=False):
    data = []
    for r in rs:
        for s in spike_strengths:
            nn = NeuralNetwork()
            axon = nn.create_axon(release_time_factor=r,
                        replenish_rate=0.0,
                        reuptake_rate=0.0,
                        verbose=args.verbose)
            axon_data,synapse_data,dendrite_data = run(nn,
                axon=axon,
                iterations = 100,
                frequency=0,
                spike_strength=s)
            data.append(("release %s  rate: %s" % (str(r), str(s)), axon_data))
            if print_synapse:
                data.append(("synapse %s  rate: %s" % (str(r), str(s)), synapse_data))
    plot(data, title="Release (release time factor)")

def axon_reuptake(rs=[0.1, 0.5, 1.0], print_synapse=False):
    data = []
    for r in rs:
        nn = NeuralNetwork()
        syn = nn.create_synapse(enzyme_concentration=0.0)
        syn.add_concentration(0.5)

        axon = nn.create_axon(release_time_factor=1,
                    replenish_rate=0.0,
                    reuptake_rate=r,
                    verbose=args.verbose)
        axon.set_concentration(0.0)

        axon_data,synapse_data,dendrite_data = run(nn,
            axon=axon,
            synapse = syn,
            iterations = 50,
            frequency=0,
            spike_strength=0.0)
        data.append(("reuptake " + str(r), axon_data))
        if print_synapse: data.append(("synapse " + str(r), synapse_data))
    plot(data, title="Reuptake (reuptake rate)")

def axon_replenish(rs=[0.1, 0.5, 1.0]):
    data = []
    for r in rs:
        nn = NeuralNetwork()
        axon = nn.create_axon(release_time_factor=1,
                    replenish_rate=r,
                    reuptake_rate=0.0,
                    verbose=args.verbose)
        axon.set_concentration(0.0)

        axon_data,synapse_data,dendrite_data = run(nn,
            axon=axon,
            iterations = 50,
            frequency=0,
            spike_strength=0.0)
        data.append(("replenish " + str(r), axon_data))
    plot(data, title="Replenish (replenish rate)")

def main():
    axon_release([100], print_synapse=True)
    axon_release([10], spike_strengths=[0.1, 0.25, 0.5, 0.75, 1.0], print_synapse=False)
    axon_release()

    axon_reuptake([0.1], print_synapse=True)
    axon_reuptake()

    axon_replenish()

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synapse->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
