import argparse
from plot import plot
from synapse import Synapse
from molecule import Molecule_IDs

def run(synapse, increase=False, decrease=False, sustain=False, record_components = [], molecule = Molecule_IDs.GLUTAMATE,
        iterations=100, frequency=None, spike_strength=1.0, sample_rate=1, verbose=False):
    data = [(name,[]) for name,component in record_components]

    def record(time):
        for i,component in enumerate(record_components):
            data[i][1].append(component[1].get_concentration(molecule))

        if verbose:
            print(("%5d, %.4f" % (time, spike_strength)) + \
                ",".join("%-20s" % str(x[-1]) for x in data))

    def fire(time):
       try: synapse.axons[0].fire(spike_strength)
       except IndexError: pass
        
    if increase: spike_strength /= 8
    if frequency == 0: fire(0)
    if sustain:
        time_changes = [0.1, 0.2, 0.3, 0.4]
    else:
        time_changes = [0.25, 0.5, 0.75]

    for t in xrange(iterations):
        synapse.step(t)
        if t % sample_rate == 0: record(t)
        if frequency and frequency > 0:
            if t % frequency == 0: fire(t)
        if decrease:
            for time_change in time_changes:
                if t == iterations*_change: spike_strength /= 2
        elif increase:
            for time_change in time_changes:
                if t == iterations*time_change: spike_strength *= 2

    return data

def main():
    print_axon=True
    print_synaptic_cleft=True
    print_dendrite=True

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

    record_components = []
    if print_axon:
        record_components.append((
            "axon", axon))
    if print_synaptic_cleft:
        record_components.append((
            "synaptic cleft", syn.synaptic_cleft))
    if print_dendrite:
        record_components.append((
            "dendrite", dendrite))

    data = run(syn, record_components=record_components,
        iterations = 100,
        frequency=0,
        spike_strength=1.0)

    if not args.silent:
        plot(data, title="Simple spike release")

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
