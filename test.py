import argparse

from plot import plot

from molecule import Molecules
from axon import Axon
from synapse import Synapse
from dendrite import Dendrite

def run_simulation(axon=None, syn=None, dendrite=None,
        iterations=50, spike_rate=1000, spike_strength=1.0,
        mol_id=Molecules.GLUTAMATE, graded=True, verbose=False):
    if syn is None:
        syn = Synapse(0.25)
    if axon is None:
        axon = Axon(mol_id=mol_id, verbose=True)
    if dendrite is None:
        dendrite = Dendrite(mol_id=mol_id, initial_size=0.25)

    axon.set_synapse(syn)
    dendrite.set_synapse(syn)

    axon_data = []
    synapse_data = []
    dendrite_data = []

    rate = 0.0
    for time in xrange(iterations):
        if time % spike_rate == 0:
            rate = spike_strength
            if not graded:
                axon.fire(rate, time)

        syn.step(time)
        if graded: axon.fire(rate, time)
        axon.step(time)
        dendrite.step(time)

        axon_data.append(axon.concentration)
        synapse_data.append(syn.concentrations[mol_id])
        dendrite_data.append(dendrite.concentration)
        if verbose:
            output = (time,rate,axon.concentration,syn.concentrations[mol_id],dendrite.concentration)
            print(",".join("%-20s" % str(x) for x in output))

    return axon_data,synapse_data,dendrite_data

def main():
    args = set_options()

    data = []
    for r in [0, 5, 10, 100]:
    #for r in [5]:
        axon_data,synapse_data,dendrite_data = run_simulation(
            dendrite = Dendrite(release_time_factor=r, initial_size=0.0),
            axon = Axon(release_time_factor=10, replenish_time_factor=r, reuptake_size=0.5, verbose=True),
            iterations=args.iterations, graded=False, verbose=args.verbose)

        # Plot data
        if args.all or args.axon: data.append(("axon", axon_data))
        if args.all or args.synapse: data.append(("synapse", synapse_data))
        if args.all or args.dendrite: data.append(("dendrite " + str(r), dendrite_data))
    plot(data, args.filename)


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
