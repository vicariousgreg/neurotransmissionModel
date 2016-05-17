import argparse

from plot import plot

from simulation import simulate_synapse
from synapse import Synapse

def synaptic_cleft_metabolize(rs=[0.01, 0.1, 0.5, 1.0, 2.0]):
    data = []

    for r in rs:
        syn = Synapse(verbose=args.verbose)
        syn.set_enzyme_concentration(r)
        syn.synaptic_cleft.set_concentration(1.0)

        record_components = [(
            "metabolize %s" % str(r),
            syn.synaptic_cleft)]

        data += simulate_synapse(syn, record_components=record_components, iterations=1000)
    if not args.silent:
        plot(data, title="Metabolize (enzyme concentration)") #, file_name="metabolize.jpg")

def main():
    synaptic_cleft_metabolize()

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
