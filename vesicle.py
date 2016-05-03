# Vesicle Model
#
# Models the vesicles of presynaptic neurons, which pump neurotransmitters 
#     into the synapse.
#
# Release follows an inverse exponential rate (e^-x).

from math import exp

class Vesicle:
    def __init__(self, mol_id, synapse):
        """
        Vesicles keep track of activation strengths and ages.
        """
        self.mol_id = mol_id
        self.synapse = synapse
        self.potential_strengths = []
        self.potential_times = []
        self.time = 0

    def step(self):
        """
        Runs a time step.
        Molecules are cleared from the synapse every time step.
        The amount cleared depends on the concentrations of molecules
            and their corresponding enzymes.
        """
        self.time += 1

        for strength,time_tag in zip(self.potential_strengths, self.potential_times):
            age = self.time - time_tag
            mol_count = strength*exp(-float(age) / 10)
            print("Releasing %f molecules" % mol_count)
            self.synapse.insert(self.mol_id, mol_count)

    def fire(self, potential):
        """
        Fires an action/graded |potential|.
        """
        self.potential_strengths.append(potential)
        self.potential_times.append(self.time)
