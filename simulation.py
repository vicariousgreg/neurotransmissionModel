from plot import plot

def run(synapse, taper=False,
        iterations=100, frequency=None, spike_strength=1.0, verbose=False):
    axon_data = []
    dendrite_data = []
    synaptic_cleft_data = []

    def record(time):
        try:
            axon_data.append(synapse.axons[0].get_concentration())
        except IndexError: pass
        synaptic_cleft_data.append(synapse.synaptic_cleft.get_concentration())
        try:
            dendrite_data.append(synapse.dendrites[0].get_concentration())
        except IndexError: pass

        if verbose:
            output = (time,spike_strength,
                synapse.axons[0].get_concentration() if len(synapse.axon)>0 else "",
                synapse.synaptic_cleft.get_concentration(),
                synapse.dendrites[0].get_concentration() if len(synapse.dendrites)>0 else "")
            print(",".join("%-20s" % str(x) for x in output))

    def fire(time):
       try: synapse.axons[0].fire(spike_strength, time)
       except IndexError: pass
        
    if frequency == 0: fire(0)
    for t in xrange(iterations):
        synapse.step(t)
        record(t)
        if frequency and frequency > 0:
            if t % frequency == 0: fire(t)
        if taper:
            if t == iterations/2: spike_strength /= 2
            if t == iterations*0.75: spike_strength /= 2
    record(t)

    return axon_data,synaptic_cleft_data,dendrite_data
