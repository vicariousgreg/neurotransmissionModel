import argparse
from plot import plot
from synapse import Synapse

def run(synapse, taper=False,
        iterations=100, frequency=None, spike_strength=1.0, verbose=False):
    axon_data = []
    dendrite_data = []
    synaptic_cleft_data = []

    def record(time):
        try:
            axon_data.append(synapse.axons[0].get_concentration())
        except IndexError: pass
        synaptic_cleft_data.append(synapse.synaptic_cleft.get_concentration())
        try:
            dendrite_data.append(synapse.dendrites[0].get_concentration())
        except IndexError: pass

        if verbose:
            output = (time,spike_strength,
                synapse.axons[0].get_concentration() if len(synapse.axons)>0 else "",
                synapse.synaptic_cleft.get_concentration(),
                synapse.dendrites[0].get_concentration() if len(synapse.dendrites)>0 else "")
            print(",".join("%-20s" % str(x) for x in output))

    def fire(time):
       try: synapse.axons[0].fire(spike_strength, time)
       except IndexError: pass
        
    if frequency == 0: fire(0)
    for t in xrange(iterations):
        synapse.step(t)
        record(t)
        if frequency and frequency > 0:
            if t % frequency == 0: fire(t)
        if taper:
            if t == iterations*0.25: spike_strength /= 2
            if t == iterations*0.5: spike_strength /= 2
            if t == iterations*0.75: spike_strength /= 2
    record(t)

    return axon_data,synaptic_cleft_data,dendrite_data

def main():
    syn = Synapse(verbose=args.verbose)
    axon = syn.create_axon(release_time_factor=20,
                replenish_rate=0.1,
                reuptake_rate=0.5,
                capacity=0.5,
                verbose=args.verbose)
    dendrite = syn.create_dendrite(
                density=1.0,
                verbose=args.verbose)
    syn.set_enzyme_concentration(1.0)
    axon_data,synaptic_cleft_data,dendrite_data = run(syn,
        iterations = 100,
        frequency=0,
        spike_strength=0.1)

    data = []
    print_axon=True
    print_synaptic_cleft=True
    print_dendrite=True
    if print_axon:
        data.append(("axon", axon_data))
    if print_synaptic_cleft:
        data.append(("synapse", synaptic_cleft_data))
    if print_dendrite:
        data.append(("dendrite", dendrite_data))
    if not args.silent:
        plot(data, title="Short Term Depression (firing rate, strength)")

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
