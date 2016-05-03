from molecule import Molecules
from vesicle import Vesicle
from synapse import Synapse
from receptor import Receptor

syn = Synapse(0.25, verbose=False)
v = Vesicle(Molecules.GLUTAMATE, syn, verbose=False)
r = Receptor(Molecules.GLUTAMATE, syn, 0.25, verbose=False)

for time in xrange(10000):
    if time % 10 == 0:
        print("*")
        v.fire(0.25, time)
    v.step(time)
    syn.step(time)
    r.step(time)
