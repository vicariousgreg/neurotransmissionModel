import argparse

from plot import plot

from simulation import run
from synapse import Synapse
from molecule import Receptors

def dendrite_bind(rs=[0.1, 0.5, 1.0], print_synaptic_cleft=False):
    data = []
    for r in rs:
        syn = Synapse(verbose=args.verbose)
        dendrite = syn.create_dendrite(density=1.0, verbose=args.verbose)
        syn.synaptic_cleft.set_concentration(r)

        record_components = [("bind %s" % str(r), dendrite)]
        if print_synaptic_cleft:
            record_components.append((
                "synaptic cleft %s" % str(r),
                syn.synaptic_cleft))

        data += run(syn, record_components=record_components,
            iterations=100, verbose=args.verbose)
    if not args.silent:
        plot(data, title="Bind (synaptic_cleft concentration)")

def dendrite_release(print_synaptic_cleft=False):
    data = []

    syn = Synapse(verbose=args.verbose)
    dendrite = syn.create_dendrite(density=1.0, verbose=args.verbose)
    dendrite.set_concentration(1.0)

    record_components = [("release", dendrite)]
    if print_synaptic_cleft:
        record_components.append((
            "synaptic cleft %s" % str(r),
            syn.synaptic_cleft))

    data += run(syn, record_components=record_components,
        iterations=25, verbose=args.verbose)
    if not args.silent:
        plot(data, title="Release (release rate)")

def multiple_dendrites(rs=[0.1], print_synaptic_cleft=False):
    data = []
    for r in rs:
        syn = Synapse(verbose=args.verbose)
        dendrite1 = syn.create_dendrite(receptor=Receptors.AMPA, density=0.1, verbose=args.verbose)
        dendrite2 = syn.create_dendrite(receptor=Receptors.NMDA, density=0.1, verbose=args.verbose)
        syn.synaptic_cleft.set_concentration(r)

        record_components = [("bind1 %s" % str(r), dendrite1),
                             ("bind2 %s" % str(r), dendrite2)]
        if print_synaptic_cleft:
            record_components.append((
                "synaptic cleft %s" % str(r),
                syn.synaptic_cleft))

        data += run(syn, record_components=record_components,
            iterations=100, verbose=args.verbose)
    if not args.silent:
        plot(data, title="Bind (synaptic_cleft concentration)")

def main():
    dendrite_bind(print_synaptic_cleft=False)
    #dendrite_release()
    multiple_dendrites()

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synaptic_cleft->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")
    parser.add_argument("-s", "--silent", action = "store_true", help = 
    """do not display graphs""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
