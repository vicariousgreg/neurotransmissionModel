import argparse

from plot import plot

from molecule import Molecules
from axon import Axon
from dendrite import Dendrite
from synapse import Synapse

def run_simulation(axon=None, syn=None, dendrite=None,
        iterations=100, frequency=10, spike_strength=1.0):
    if syn is None: syn = Synapse(0.0)
    syn.connect(axon)
    syn.connect(dendrite)
    axon_data = []
    synapse_data = []
    dendrite_data = []
    rate = 0.0

    def record(time):
        axon_data.append(axon.get_concentration())
        synapse_data.append(syn.get_concentration())
        dendrite_data.append(dendrite.get_concentration())

        if args.verbose:
            output = (time,rate,axon.get_concentration(),syn.get_concentration(),dendrite.get_concentration())
            print(",".join("%-20s" % str(x) for x in output))

    for t in xrange(iterations):
        if t % frequency == 0: axon.fire(spike_strength, t)
        if t == iterations/2: spike_strength /= 2
        if t == iterations*0.75: spike_strength /= 2
        record(t)
        if t % 3 == 0:axon.step(t)
        if t % 3 == 1:syn.step(t)
        if t % 3 == 2:dendrite.step(t)
    record(t)

    return axon_data,synapse_data,dendrite_data

def short_term_depression(rs=[1,5,10, 15], spike_strengths=[0.5],
        print_axon=False, print_synapse=False, print_dendrite=True):
    #data = []
    for r in rs:
        for s in spike_strengths:
            axon = Axon(release_time_factor=10,
                        replenish_rate=0.5,
                        reuptake_rate=1.0,
                        capacity=0.25,
                        verbose=args.verbose)
            dendrite = Dendrite(release_rate=0.5,
                        initial_size=0.5,
                        verbose=args.verbose)
            synapse = Synapse(0.1)
            axon_data,synapse_data,dendrite_data = run_simulation(
                axon=axon,
                syn=synapse,
                dendrite=dendrite,
                iterations = args.iterations,
                frequency=r,
                spike_strength=s)

            data = []
            if print_axon:
                data.append(("axon %s  rate: %s" % (str(r), str(s)), axon_data))
            if print_synapse:
                data.append(("synapse %s  rate: %s" % (str(r), str(s)), synapse_data))
            if print_dendrite:
                data.append(("dendrite %s  rate: %s" % (str(r), str(s)), dendrite_data))
            plot(data, title="Short Term Depression (firing rate, strength)")

def main():
    short_term_depression(#rs=[5],
        print_axon=True,
        print_synapse=True,
        print_dendrite=True)

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synapse->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")
    parser.add_argument("-i", "--iterations", type = int, default = 100, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
