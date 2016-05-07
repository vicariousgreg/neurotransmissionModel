# Dendrite Model
#
# Models a receptor pool of a postsynaptic neuron, to which neurotransmitters
#     from the synaptic cleft bind, modifying the membrane potential of the cell.

from math import exp
from stochastic import beta
from membrane import Membrane

from molecule import Molecules, Analogs

class Dendrite(Membrane):
    def __init__(self, initial_size=1.0, mol_id=Molecules.GLUTAMATE,
                    environment=None, verbose=False):
        """
        Dendrites get neurotransmitters from a synaptic cleft and release them
            back over time.

        |mol_id| is the identifier for the neurotransmitter to be bound.
        |initial_size| is the initial size of the receptor pool.
        """
        if initial_size > 1.0: raise ValueError
        Membrane.__init__(self, mol_id, 0.0, environment)

        self.size = initial_size
        self.verbose = verbose
        self.destination = None

    def get_available_spots(self):
        return self.size - self.get_total_concentration()

    def step(self, time):
        """
        Runs a time step.
        Releases molecules.
        """
        self.release()

    def release(self):
        for mol_id in self.analogs:
            available = self.get_concentration(mol_id)
            if available == 0.0: continue

            # Stochastically sample bound molecules
            released = beta(available, rate=1.0-Analogs[mol_id][2])

            if self.verbose: print("Removed %f molecules" % released)

            self.remove_concentration(released, mol_id)
            if self.destination:
                self.destination.add_concentration(released, mol_id=mol_id)
