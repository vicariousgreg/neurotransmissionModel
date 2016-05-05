import argparse

from plot import plot

from molecule import Molecules
from axon import Axon
from synapse import Synapse

def run_simulation(axon, syn=None, iterations=100, spike_strength=1.0):
    if syn is None: syn = Synapse(0.0)
    syn.connect(axon)
    axon_data = []
    synapse_data = []
    rate = 0.0

    def record(time):
        axon_data.append(axon.get_concentration())
        synapse_data.append(syn.get_concentration())

        if args.verbose:
            output = (time,rate,axon.get_concentration(),syn.get_concentration())
            print(",".join("%-20s" % str(x) for x in output))

    axon.fire(spike_strength, 0)
    for t in xrange(iterations):
        record(t)
        syn.step(t)
        axon.step(t)
    record(t)

    return axon_data,synapse_data

def axon_release(rs=[1,5,10, 100, 1000], spike_strengths=[1.0], print_synapse=False):
    data = []
    for r in rs:
        for s in spike_strengths:
            axon = Axon(release_time_factor=r,
                        replenish_rate=0.0,
                        reuptake_rate=0.0,
                        verbose=args.verbose)
            axon_data,synapse_data = run_simulation(
                axon,
                iterations = 100,
                spike_strength=s)
            data.append(("release %s  rate: %s" % (str(r), str(s)), axon_data))
            if print_synapse:
                data.append(("synapse %s  rate: %s" % (str(r), str(s)), synapse_data))
    plot(data, title="Release")

def axon_reuptake(rs=[0.1, 0.5, 1.0], print_synapse=False):
    data = []
    for r in rs:
        syn = Synapse(0.0)
        syn.add_concentration(0.5)

        axon = Axon(release_time_factor=1,
                    replenish_rate=0.0,
                    reuptake_rate=r,
                    verbose=args.verbose)
        axon.set_concentration(0.0)

        axon_data,synapse_data = run_simulation(
            axon,
            syn = syn,
            iterations = 50,
            spike_strength=0.0)
        data.append(("reuptake " + str(r), axon_data))
        if print_synapse: data.append(("synapse " + str(r), synapse_data))
    plot(data, title="Reuptake")

def axon_replenish(rs=[0.1, 0.5, 1.0]):
    data = []
    for r in rs:
        axon = Axon(release_time_factor=1,
                    replenish_rate=r,
                    reuptake_rate=0.0,
                    verbose=args.verbose)
        axon.set_concentration(0.0)

        axon_data,synapse_data = run_simulation(
            axon,
            iterations = 50,
            spike_strength=0.0)
        data.append(("replenish " + str(r), axon_data))
    plot(data, title="Replenish")

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
