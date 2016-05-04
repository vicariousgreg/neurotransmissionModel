import argparse

from plot import plot

from molecule import Molecules
from axon import Axon
from synapse import Synapse

def run_simulation(axon, syn=None, iterations=100,
        spike_strength=1.0, verbose=False):
    if syn is None: syn = Synapse(0.0)

    axon.set_synapse(syn)
    axon_data = []
    synapse_data = []
    rate = 0.0

    for time in xrange(iterations):
        if time == 0: axon.fire(spike_strength, time)
        syn.step(time)
        axon.step(time)

        axon_data.append(axon.concentration)
        synapse_data.append(syn.concentrations[Molecules.GLUTAMATE])

        if verbose:
            output = (time,rate,axon.concentration,syn.concentrations[Molecules.GLUTAMATE])
            print(",".join("%-20s" % str(x) for x in output))
    return axon_data,synapse_data

def axon_release(rs=[1,5,10, 100, 1000], print_synapse=False):
    data = []
    for r in rs:
        axon_data,synapse_data = run_simulation(
            Axon(release_time_factor=r, replenish_rate=0.0, reuptake_rate=0.0, verbose=True),
            iterations = 100, verbose=True)
        data.append(("release " + str(r), axon_data))
        if print_synapse: data.append(("synapse " + str(r), synapse_data))
    plot(data)

def axon_reuptake(rs=[0.1, 0.5, 1.0], print_synapse=False):
    data = []
    for r in rs:
        syn = Synapse(0.0)
        syn.insert(0.5)

        axon = Axon(release_time_factor=1, replenish_rate=0.0, reuptake_rate=r, verbose=True)
        axon.concentration = 0.5

        axon_data,synapse_data = run_simulation(
            axon,
            syn = syn,
            iterations = 50,
            verbose=True, spike_strength=0.0)
        data.append(("reuptake " + str(r), axon_data))
        if print_synapse: data.append(("synapse " + str(r), synapse_data))
    plot(data)

def axon_replenish(rs=[0.1, 0.5, 1.0]):
    data = []
    for r in rs:
        axon = Axon(release_time_factor=1, replenish_rate=r, reuptake_rate=0.0, verbose=True)
        axon.concentration = 0.5

        axon_data,synapse_data = run_simulation(
            axon,
            iterations = 50,
            verbose=True, spike_strength=0.0)
        data.append(("replenish " + str(r), axon_data))
    plot(data)

def main():
    args = set_options()

    axon_release([100], print_synapse=True)
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
    parser.add_argument("-a", "--all", action = "store_true", help = 
    """plot all recordings""")
    parser.add_argument("-x", "--axon", action = "store_true", help = 
    """plot axon recording""")
    parser.add_argument("-s", "--synapse", action = "store_true", help = 
    """plot synapse recording""")
    parser.add_argument("-d", "--dendrite", action = "store_true", help = 
    """plot dendrite recording""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")
    parser.add_argument("-i", "--iterations", type = int, default = 1, help =
    """number of iterations""")

    parser.add_argument("-f", "--filename", type = str, default = None, help =
    """name of location to save plot to""")

    return parser.parse_args()

if __name__ == "__main__":
    main()
