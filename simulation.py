from plot import plot

from neural_network import NeuralNetwork

def run(network, axon=None, synapse=None, dendrite=None, taper=False,
        iterations=100, frequency=None, spike_strength=1.0, verbose=False):
    if synapse is None: synapse = network.create_synapse(enzyme_concentration=0.0)
    if axon:
        synapse.connect(axon)
    axon_data = []
    if dendrite:
        synapse.connect(dendrite)
    dendrite_data = []
    synapse_data = []

    def record(time):
        if axon: axon_data.append(axon.get_concentration())
        synapse_data.append(synapse.get_concentration())
        if dendrite: dendrite_data.append(dendrite.get_concentration())

        if verbose:
            output = (time,spike_strength,
                axon.get_concentration() if axon else "",
                synapse.get_concentration(),
                dendrite.get_concentration() if dendrite else "")
            print(",".join("%-20s" % str(x) for x in output))

    components = [x for x in (axon,synapse,dendrite) if x]
    if frequency == 0: axon.fire(spike_strength, 0)
    for t in xrange(iterations):
        network.step(t)
        record(t)
        if frequency and frequency > 0:
            if t % frequency == 0: axon.fire(spike_strength, t)
        if taper:
            if t == iterations/2: spike_strength /= 2
            if t == iterations*0.75: spike_strength /= 2
    record(t)

    return axon_data,synapse_data,dendrite_data
