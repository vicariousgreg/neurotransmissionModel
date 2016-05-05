import argparse

from plot import plot

from molecule import Molecules
from synapse import Synapse
from dendrite import Dendrite

def run_simulation():
    syn = Synapse(0.0)
    syn.set_concentration(1.0)
    dendrite = Dendrite(release_rate=1, mol_id=Molecules.GLUTAMATE, initial_size=1.0, verbose=True)
    syn.connect(dendrite)
    synapse_data = []
    dendrite_data = []
    rate = 0.0

    def record(time):
        synapse_data.append(syn.get_concentration(Molecules.GLUTAMATE))
        dendrite_data.append(dendrite.get_concentration())

    for t in xrange(100):
        record(t)
        syn.step(t)
        dendrite.step(t)
    record(t)

    return synapse_data, dendrite_data

def main():
    syn_data, dend_data = run_simulation()
    data = [("synapse", syn_data), ("dendrite", dend_data)]
    plot(data, title="Replenish")

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synapse->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
