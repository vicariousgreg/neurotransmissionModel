import argparse

from plot import plot

from synaptic_cleft import SynapticCleft
from dendrite import Dendrite
from simulation import run
from synapse import Synapse

def dendrite_bind(rs=[0.1, 0.5, 1.0], print_synaptic_cleft=False):
    data = []
    for r in rs:
        syn = Synapse(verbose=args.verbose)
        dendrite = syn.create_dendrite(release_rate=0, initial_size=1.0, verbose=args.verbose)
        syn.synaptic_cleft.set_concentration(r)

        axon_data,synaptic_cleft_data, dendrite_data = run(syn,
            iterations=100, verbose=args.verbose)
        data.append(("bind " + str(r), dendrite_data))
        if print_synaptic_cleft: data.append(("synaptic_cleft " + str(r), synaptic_cleft_data))
    plot(data, title="Bind (synaptic_cleft concentration)")

def dendrite_release(rs=[0.1, 0.5, 1, 5], print_synaptic_cleft=False):
    data = []
    for r in rs:
        syn = Synapse(verbose=args.verbose)
        dendrite = syn.create_dendrite(release_rate=r, initial_size=1.0, verbose=args.verbose)
        dendrite.set_concentration(1.0)

        axon_data,synaptic_cleft_data, dendrite_data = run(syn,
            iterations=25, verbose=args.verbose)
        data.append(("release " + str(r), dendrite_data))
        if print_synaptic_cleft: data.append(("synaptic_cleft " + str(r), synaptic_cleft_data))
    plot(data, title="Release (release rate)")

def main():
    dendrite_bind(print_synaptic_cleft=False)
    dendrite_release()

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synaptic_cleft->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
