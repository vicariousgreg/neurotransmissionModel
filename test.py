from molecule import Molecules
from axon import Axon
from synapse import Synapse
from receptor import Receptor

mol_id = Molecules.GLUTAMATE

syn = Synapse(0.25, verbose=False)
axon = Axon(mol_id, syn, verbose=False)
rec = Receptor(mol_id, syn, 0.25, verbose=False)

output = []
for time in xrange(10000):
    fired= False
    if time % 10 == 0:
        fired = True
        #print("*")
        axon.fire(0.25, time)
    axon.step(time)
    syn.step(time)
    rec.step(time)

    output = (time,"x" if fired else " ",axon.concentration,syn.concentrations[mol_id],rec.concentration)
    print(",".join(str(x) for x in output))
