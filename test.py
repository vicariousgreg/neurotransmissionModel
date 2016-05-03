from molecule import Molecules
from vesicle import Vesicle
from synapse import Synapse

syn = Synapse()
v = Vesicle(Molecules.GLUTAMATE, syn)

v.fire(1.0)

for _ in xrange(10):
    v.step()
    syn.step()
    print(syn.concentrations[Molecules.GLUTAMATE])
    print("")
