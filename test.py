from molecule import Molecules
from axon import Axon
from synapse import Synapse
from dendrite import Dendrite

mol_id = Molecules.GLUTAMATE

syn = Synapse(0.25, verbose=False)
axon = Axon(mol_id, syn, verbose=False)
dendrite = Dendrite(mol_id, syn, 0.25, verbose=False)

output = []
spikes = dict([
    (0, 0.1),
    (25, 0.25),
    (50, 0.30),
    (75, 0.5),
    (100, 0.9),
    (150, 0.25),
    (200, 0.1)]
)

#spikes = dict([(0,0.1)])
#spikes = dict([(0,1.0)])
#spikes = dict([(0,0.5)])

rate = 0.0
for time in xrange(400):
    if time in spikes:
        rate = spikes[time]
        #print("\nRate changed to: %f\n" % rate)

    syn.step(time)
    #if time % 25 == 0: axon.fire(rate, time)
    axon.fire(rate, time)
    axon.step(time)
    dendrite.step(time)

    if time == 50:
        dendrite.size = 0.5
        #print("\nSize changed to 0.5")
    if time == 100:
        dendrite.size = 0.75
        #print("\nSize changed to 0.75")
    if time == 150:
        dendrite.size = 1.0
        #print("\nSize changed to 1.0")

    output = (time,rate,axon.concentration,syn.concentrations[mol_id],dendrite.concentration)
    print(",".join("%-20s" % str(x) for x in output))
