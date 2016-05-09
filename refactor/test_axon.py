import argparse

from plot import plot

from simulation import run
from synapse import Synapse

def axon_release(rs=[1,5,10, 100, 1000], spike_strengths=[1.0], print_synaptic_cleft=False):
    data = []
    for r in rs:
        for s in spike_strengths:
            syn = Synapse(verbose=args.verbose)
            axon = syn.create_axon(release_time_factor=r,
                        replenish_rate=0.0,
                        reuptake_rate=0.0,
                        verbose=args.verbose)

            record_components = [("release %s  rate: %s" % (str(r), str(s)), axon)]
            if print_synaptic_cleft:
                record_components.append((
                    "synaptic cleft %s  rate: %s" % (str(r), str(s)),
                    syn.synaptic_cleft))

            data += run(syn,
                record_components = record_components,
                iterations = 100,
                frequency=0,
                spike_strength=s)
    if not args.silent: plot(data, title="Release (release time factor)")

def axon_reuptake(rs=[0.1, 0.5, 1.0], print_synaptic_cleft=False):
    data = []
    for r in rs:
        syn = Synapse(verbose=args.verbose)
        syn.synaptic_cleft.add_concentration(0.5)

        axon = syn.create_axon(release_time_factor=1,
                    replenish_rate=0.0,
                    reuptake_rate=r,
                    verbose=args.verbose)
        axon.set_concentration(0.0)

        record_components = [("reuptake %s" % str(r), axon)]
        if print_synaptic_cleft:
            record_components.append((
                "synaptic cleft %s" % str(r),
                syn.synaptic_cleft))

        data += run(syn,
            record_components = record_components,
            iterations = 100,
            frequency=0,
            spike_strength=0.0)
    if not args.silent: plot(data, title="Reuptake (reuptake rate)")

def axon_replenish(rs=[0.1, 0.5, 1.0]):
    data = []
    for r in rs:
        syn = Synapse(verbose=args.verbose)
        axon = syn.create_axon(release_time_factor=1,
                    replenish_rate=r,
                    reuptake_rate=0.0,
                    verbose=args.verbose)
        axon.set_concentration(0.0)

        record_components = [("replenish %s" % str(r), axon)]

        data += run(syn,
            record_components = record_components,
            iterations = 50,
            frequency=0,
            spike_strength=0.0)
    if not args.silent: plot(data, title="Replenish (replenish rate)")

def main():
    axon_release([100], print_synaptic_cleft=True)
    axon_release([10], spike_strengths=[0.1, 0.25, 0.5, 0.75, 1.0], print_synaptic_cleft=False)
    axon_release()

    axon_reuptake([0.1], print_synaptic_cleft=True)
    axon_reuptake()

    axon_replenish()

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
