import argparse

from plot import plot

from synaptic_cleft import SynapticCleft
from axon import Axon
from dendrite import Dendrite
from simulation import run
from synapse import Synapse

def synaptic_cleft_metabolize(rs=[0.01, 0.1, 0.5, 1.0]):
    data = []

    for r in rs:
        syn = Synapse(verbose=args.verbose)
        synapse.set_enzyme_concentration(r)
        synapse.synaptic_cleft.set_concentration(1.0)

        axon_data,synaptic_cleft_data,dendrite_data = run(syn, iterations=100)
        data.append(("metabolize " + str(r), synaptic_cleft_data))
    plot(data, title="Metabolize (enzyme concentration)")

def synaptic_cleft_bind(rs=[0.01, 0.1, 0.5, 1.0]):
    data = []

    for r in rs:
        syn = Synapse(verbose=args.verbose)
        dendrite = syn.create_dendrite(release_rate=0, initial_size=r)
        synapse.synaptic_cleft.set_concentration(1.0)

        axon_data,synaptic_cleft_data,dendrite_data = run(syn, iterations=50)
        data.append(("bind " + str(r), synaptic_cleft_data))
    plot(data, title="Bind (dendrite density)")

def main():
    synaptic_cleft_metabolize()
    synaptic_cleft_bind()

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
