import argparse

from plot import plot

from molecule import Molecules
from axon import Axon
from synapse import Synapse
from dendrite import Dendrite

def main():
    args = set_options()

    mol_id = Molecules.GLUTAMATE

    syn = Synapse(0.25, verbose=False)
    axon = Axon(mol_id, syn, verbose=False)
    dendrite = Dendrite(mol_id, syn, 0.25, verbose=False)

    output = []
    spikes = dict([
        (0, 0.1),
        (25, 0.25),
        (50, 0.30),
        (75, 0.5),
        (100, 0.9),
        (150, 0.25),
        (200, 0.1)]
    )

    #spikes = dict([(0,0.1)])
    #spikes = dict([(0,1.0)])
    #spikes = dict([(0,0.5)])

    axon_data = []
    synapse_data = []
    dendrite_data = []

    rate = 0.0
    for time in xrange(args.iterations):
        if time in spikes:
            rate = spikes[time]
            #print("\nRate changed to: %f\n" % rate)

        syn.step(time)
        #if time % 25 == 0: axon.fire(rate, time)
        axon.fire(rate, time)
        axon.step(time)
        dendrite.step(time)

        if time == 50:
            dendrite.size = 0.5
            #print("\nSize changed to 0.5")
        if time == 100:
            dendrite.size = 0.75
            #print("\nSize changed to 0.75")
        if time == 150:
            dendrite.size = 1.0
            #print("\nSize changed to 1.0")

        axon_data.append(axon.concentration)
        synapse_data.append(syn.concentrations[mol_id])
        dendrite_data.append(dendrite.concentration)
        output = (time,rate,axon.concentration,syn.concentrations[mol_id],dendrite.concentration)
        #print(",".join("%-20s" % str(x) for x in output))

    # Plot data
    data = []
    if args.all or args.axon: data.append(("axon", axon_data))
    if args.all or args.synapse: data.append(("synapse", synapse_data))
    if args.all or args.dendrite: data.append(("dendrite", dendrite_data))

    plot(data)

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

    return parser.parse_args()

if __name__ == "__main__":
    main()
