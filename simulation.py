import argparse
from plot import plot
from synapse import Synapse
from molecule import Molecule_IDs

def simulate_synapse(synapse, record_components = [], molecule = Molecule_IDs.GLUTAMATE,
        iterations=100, verbose=False):
    data = [(name,[]) for name,component in record_components]

    def record(time):
        for i,component in enumerate(record_components):
            data[i][1].append(component[1].get_concentration(molecule))
        if verbose: ",".join("%-20s" % str(x[-1]) for x in data)

    for t in xrange(iterations):
        synapse.step(t)
        record(t)

    return data
