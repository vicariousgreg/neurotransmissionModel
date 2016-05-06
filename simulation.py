from plot import plot

from neural_network import NeuralNetwork

def run(network, axon=None, synaptic_cleft=None, dendrite=None, taper=False,
        iterations=100, frequency=None, spike_strength=1.0, verbose=False):
    if synaptic_cleft is None:
        synaptic_cleft = network.create_synaptic_cleft(enzyme_concentration=0.0)
    if axon:
        synaptic_cleft.connect(axon)
    axon_data = []
    if dendrite:
        synaptic_cleft.connect(dendrite)
    dendrite_data = []
    synaptic_cleft_data = []

    def record(time):
        if axon: axon_data.append(axon.get_concentration())
        synaptic_cleft_data.append(synaptic_cleft.get_concentration())
        if dendrite: dendrite_data.append(dendrite.get_concentration())

        if verbose:
            output = (time,spike_strength,
                axon.get_concentration() if axon else "",
                synaptic_cleft.get_concentration(),
                dendrite.get_concentration() if dendrite else "")
            print(",".join("%-20s" % str(x) for x in output))

    components = [x for x in (axon,synaptic_cleft,dendrite) if x]
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

    return axon_data,synaptic_cleft_data,dendrite_data
