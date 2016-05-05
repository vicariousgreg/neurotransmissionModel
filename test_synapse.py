import argparse

from plot import plot

from synapse import Synapse
from axon import Axon
from dendrite import Dendrite
from simulation import run

def run_simulation(syn, axon=None, dendrite=None, iterations=100, verbose=False):
    if dendrite:
        syn.connect(dendrite)
    if axon:
        syn.connect(axon)

    synapse_data = []

    def record(time):
        synapse_data.append(syn.get_concentration())

        if args.verbose:
            output = (time,
                axon.get_concentration() if axon else "",
                syn.get_concentration(),
                dendrite.get_concentration() if dendrite else "")
            print(",".join("%-20s" % str(x) for x in output))

    for t in xrange(iterations):
        record(t)
        try: axon.step(t)
        except AttributeError: pass
        syn.step(t)
        try: dendrite.step(t)
        except AttributeError: pass
    record(t)

    return synapse_data

def synapse_metabolize(rs=[0.01, 0.1, 0.5, 1.0]):
    data = []
    for r in rs:
        syn = Synapse(r)
        syn.set_concentration(1.0)

        axon_data,synapse_data,dendrite_data = run(synapse=syn, iterations=100)
        data.append(("metabolize " + str(r), synapse_data))
    plot(data, title="Metabolize (enzyme concentration)")

def synapse_bind(rs=[0.01, 0.1, 0.5, 1.0]):
    data = []

    for r in rs:
        dendrite = Dendrite(release_rate=0, initial_size=r)
        syn = Synapse(0.0)
        syn.set_concentration(1.0)

        axon_data,synapse_data,dendrite_data = run(synapse=syn, dendrite=dendrite, iterations=50)
        data.append(("bind " + str(r), synapse_data))
    plot(data, title="Bind (dendrite density)")

def main():
    synapse_metabolize()
    synapse_bind()

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
