# Synapse
#
# The synapse contains axons, dendrites, and a synaptic cleft.

from molecule import Enzymes, Molecule_IDs
from axon import Axon
from dendrite import Dendrite
from synaptic_cleft import SynapticCleft

class Synapse:
    def __init__(self, postsynaptic_id=None, initial_enzyme_concentration=0.0,
                    active_molecules=[Molecule_IDs.GLUTAMATE], verbose=False):
        """
        Creates a synapse with an initialized synaptic cleft.
        An initial enzyme concentration can be specified.

        If a single molecule is provided, we assume that it is the only
            molecule that is passed through this synapse.  It is passed into
            the synaptic cleft constructor, which will set itself up to save
            time and space by only checking for that molecule.
        """
        self.postsynaptic_id = postsynaptic_id
        self.axon = None
        self.dendrites = []
        self.probe = None

        self.synaptic_cleft = SynapticCleft(
            enzyme_concentration=initial_enzyme_concentration,
            active_molecules = active_molecules,
            verbose=verbose)

    def step(self, voltage):
        return self.axon.step(voltage)

    def activate_dendrites(self, neuron):
        for dendrite in self.dendrites:
            dendrite.activate(neuron)

    def set_probe(self, probe):
        self.probe = probe

    def record(self, time):
        if self.probe:
            data = [
                self.axon.get_concentration(),
                self.synaptic_cleft.get_total_concentration()
            ] + [dendrite.get_bound() for dendrite in self.dendrites]
            self.probe.record(tuple(data), time)

    def set_enzyme_concentration(self, e_c, enzymes=range(Enzymes.size)):
        """
        Sets the concentration of the given |enzymes| in the synaptic cleft.
        """
        for i in enzymes: self.synaptic_cleft.enzymes[i] = e_c

    def create_axon(self, **args):
        """
        Creates an axon and adds it to the synapse.
        """
        if self.axon is not None:
            raise ValueError("Cannot have two axons on one synapse!")
        axon = Axon(self.synaptic_cleft, **args)
        self.synaptic_cleft.axon = axon
        self.axon = axon
        return axon

    def create_dendrite(self, **args):
        """
        Creates a dendrite and adds it to the synapse.
        """
        dendrite = Dendrite(**args)
        self.synaptic_cleft.dendrites.append(dendrite)
        self.dendrites.append(dendrite)
        return dendrite
