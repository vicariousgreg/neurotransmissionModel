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
            self.axon_minimum = -999
            self.axon_maximum = self.soma.stable_voltage
        elif neuron_type == NeuronTypes.GANGLION:
            self.soma = Soma(environment)
            self.axon_minimum = -55.0
            self.axon_maximum = 0

        # Inputs
        self.dendrites = []
        self.gap_junctions = []
        self.active_gap_junctions = False

        # Currents
        self.current = base_current
        self.base_current = base_current
        self.ligand_current = 0.0
        self.gap_current = 0.0
        self.external_current = Value('d', 0.0)

        # Outputs
        self.axons = []
        self.probe = None

        # Active flags
        self.soma_stable = False
        self.axons_stable = []

    def set_probe(self, probe):
        self.probe = probe

    def set_external_current(self, current):
        self.external_current.value = current

    def clear_ligand_current(self):
        old = self.ligand_current.value
        self.ligand_current.value = 0.0
        return old

    def change_ligand_current(self, delta):
        self.ligand_current.value += delta

    def activate_dendrites(self):
        old_current = self.ligand_current

        # Activate the neuron from each dendrite
        # This will check the receptor type and decide how to modify the neuron
        # * This operation has side effects!
        for dendrite in self.dendrites:
            dendrite.activate(self)

        # Return stable if the current hasn't changed significantly.
        return abs(self.ligand_current - old_current) < 0.001

    def activate_gap_junctions(self, soma_voltage):
        # Check gap junctions if active
        new_gap_current = 0
        for other,conductance in self.gap_junctions:
            df = conductance*(other.soma.get_voltage() - soma_voltage)
            new_gap_current += df

        # Change current and return False for destable if different enough.
        if abs(new_gap_current - self.gap_current.value) > 0.001:
            self.gap_current = new_gap_current
            return False
        # Otherwise return stable.
        else: return True

    def step(self, time):
        soma_voltage = self.soma.get_voltage()
        old_current = self.current

        # Start with base curent.
        new_current = self.base_current

        # Add gap current.
        if self.active_gap_junctions:
            new_current += self.activate_gap_junctions(soma_voltage)

        # Add ligand current.
        new_current += self.activate_dendrites()

        # Add external current.
        new_current += self.external_current.value

        if abs(old_current - new_current) < 0.001:
            self.current = old_current
            self.stable = False

        # Activate the soma
        if not self.stable:
            stable = self.soma.step(total_current)

            # Activate the axons
            # If they are releasing, their synapse should be activated
            # The axons will cascade computation to the synaptic cleft, which
            #     will modify postsynaptic dendrites.
            for axon in self.axons:
                stable &= axon.step(self.soma.firing)

        # Record to probe.
        try: probe.record(self, time)
        except AttributeError: pass

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
                    delay=axon_delay,
                    voltage_minimum = self.axon_minimum,
                    voltage_maximum = self.axon_maximum)
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
