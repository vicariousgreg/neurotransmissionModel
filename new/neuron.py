# Neuron Model

from multiprocessing import Value
from enum import enum
from soma import Soma
from synapse import Synapse
from molecule import Transporters, Receptors
from photoreceptor import PhotoreceptorSoma

NeuronTypes = enum(
    PHOTORECEPTOR = 0,
    GANGLION = 1
)

class Neuron:
    def __init__(self, neuron_id=None, base_current=0.0,
                    neuron_type=NeuronTypes.GANGLION, environment=None):
        self.environment = environment
        self.neuron_id = neuron_id

        # Soma and axon threshold
        if neuron_type == NeuronTypes.PHOTORECEPTOR:
            self.soma = PhotoreceptorSoma(environment)
            self.axon_threshold = -9999
        elif neuron_type == NeuronTypes.GANGLION:
            self.soma = Soma(environment)
            self.axon_threshold = -55.0

        # Inputs
        self.dendrites = []
        self.gap_junctions = []
        self.active_gap_junctions = False

        # Currents
        self.base_current = base_current
        self.ligand_current = Value('d', 0.0)
        self.gap_current = Value('d', 0.0)
        self.external_current = Value('d', 0.0)

        # Soma
        self.soma = Soma(environment)

        # Outputs
        self.axons = []
        self.probes = []

        # Active flags
        self.soma_stable = False
        self.axons_stable = []

    def add_probe(self, probe):
        self.probes.append(probe)

    def set_external_current(self, current):
        self.external_current.value = current

    def clear_ligand_current(self):
        old = self.ligand_current.value
        self.ligand_current.value = 0.0
        return old

    def change_ligand_current(self, delta):
        self.ligand_current.value += delta

    def activate_dendrites(self):
        old_current = self.clear_ligand_curent()

        # Activate the neuron from each dendrite
        # This will check the receptor type and decide how to modify the neuron
        for dendrite in self.dendrites:
            dendrite.activate(self)

        return self.ligand_current.value == old_current

    def activate_gap_junctions(self, soma_voltage):
        # Check gap junctions if active
        new_gap_current = 0
        for other,conductance in self.gap_junctions:
            df = conductance*(other.soma.get_voltage() - soma_voltage)
            new_gap_current += df

        # Change current and return False for destable if different enough.
        if abs(new_gap_current - self.gap_current.value) > 0.001:
            self.gap_current.value = new_gap_current
            return False
        # Otherwise return stable.
        else: return True

    def step(self, time):
        soma_voltage = self.soma.get_voltage()
        stable_current = True

        if self.active_gap_junctions:
            stable_current &=  self.activate_gap_junctions(soma_voltage)

        stable_current &= self.activate_dendrites()

        total_current = sum(self.base_current,
            self.ligand_current.value,
            self.gap_current.value,
            self.external_current.value),

        # Activate the soma
        if not stable_current or not self.soma_stable:
            self.soma_stable = self.soma.step(total_current)

        for probe in self.probes: probe.record(self, time)

        '''
        # Activate the axons
        # If they are releasing, their synapse should be activated
        if soma_voltage < self.axon_threshold: soma_voltage = None
        for i,axon in enumerate(self.axons):
            if not axon.step(self.soma.firing):
                self.synapses_stable[i] = False

        # Cycle synapses if active.
        for i,synapse in enumerate(self.synapses):
            if not self.synapses_stable[i]:
                s = synapse.step()
                self.synapses_stable[i] = s
        '''

    @staticmethod
    def create_synapse(presynaptic, postsynaptic, active_molecules=None,
            transporter=Transporters.GLUTAMATE, receptor=Receptors.AMPA,
            enzyme_concentration=1.0,
            axon_delay=0, dendrite_strength=0.0015):
        synapse = Synapse(
            postsynaptic_id=postsynaptic.neuron_id,
            initial_enzyme_concentration=enzyme_concentration,
            active_molecules=active_molecules)
        axon = synapse.create_axon(
                    transporter=transporter,
                    replenish_rate=0.1,
                    reuptake_rate=0.5,
                    capacity=1.0,
                    delay=axon_delay)
        dendrite = synapse.create_dendrite(
                    receptor=receptor,
                    density=0.25,
                    strength=dendrite_strength)

        presynaptic.axons.append(axon)
        presynaptic.synapses.append(synapse)
        presynaptic.synapses_stable.append(True)
        postsynaptic.dendrites.append(dendrite)
        return synapse

    @staticmethod
    def create_gap_junction(presynaptic, postsynaptic, conductance):
        presynaptic.gap_junctions.append((postsynaptic,conductance))
        postsynaptic.gap_junctions.append((presynaptic,conductance))
        presynaptic.active_gap_junctions = True
        postsynaptic.active_gap_junctions = True
