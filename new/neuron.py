# Neuron Model

from multiprocessing import Value
from enum import enum
from soma import Soma, SOMA_TYPES
from synapse import Synapse
from molecule import Molecules, Transporters, Receptors

NeuronTypes = enum(
    PHOTORECEPTOR = 0,
    HORIZONTAL = 1,
    BIPOLAR = 2,
    AMACRINE = 3,
    GANGLION = 4
)

class Neuron:
    def __init__(self, neuron_id=None, base_current=0.0, record=False,
                    neuron_type=NeuronTypes.GANGLION, environment=None):
        self.environment = environment
        self.neuron_id = neuron_id
        self.synapses = []

        # Soma and axon threshold
        if neuron_type == NeuronTypes.PHOTORECEPTOR:
            self.soma = Soma(environment=environment,
                soma_type=SOMA_TYPES.PHOTORECEPTOR, record=record)
            self.spiking = False
        elif neuron_type == NeuronTypes.HORIZONTAL:
            base_current = -100
            self.soma = Soma(environment=environment,
                soma_type=SOMA_TYPES.HORIZONTAL, record=record)
            self.spiking = False
        elif neuron_type == NeuronTypes.GANGLION:
            self.soma = Soma(environment=environment,
                soma_type=SOMA_TYPES.DEFAULT, record=record)
            self.spiking = True

        # Inputs
        self.dendrites = []
        self.gap_junctions = []
        self.active_gap_junctions = False

        # Currents
        self.current = base_current
        self.base_current = base_current
        self.ligand_current = 0.0
        self.external_current = Value('d', 0.0)

        # Outputs
        self.axons = []

        # Active flags
        self.stable = False
        self.axons_stable = []

    def get_record(self):
        return self.environment.records[self.soma.env_id]

    def set_external_current(self, current):
        self.external_current.value = current

    def clear_ligand_current(self):
        old = self.ligand_current
        self.ligand_current = 0.0
        return old

    def change_ligand_current(self, delta):
        self.ligand_current += delta

    def activate_dendrites(self):
        # Activate the neuron from each dendrite
        # This will check the receptor type and decide how to modify the neuron
        # * This operation has side effects!
        self.ligand_current = 0.0
        for dendrite in self.dendrites:
            dendrite.activate(self)
        return self.ligand_current

    def activate_gap_junctions(self, soma_voltage):
        # Check gap junctions if active
        gap_current = 0
        for other,conductance in self.gap_junctions:
            df = conductance*(other.soma.get_voltage() - soma_voltage)
            gap_current += df
        return gap_current

    def step(self, time):
        soma_voltage = self.soma.get_voltage()
        old_current = self.current

        ### Calculate current
        # Start with base curent.
        new_current = self.base_current

        # Add gap current.
        if self.active_gap_junctions:
            new_current += self.activate_gap_junctions(soma_voltage)

        # Add ligand current.
        new_current += self.activate_dendrites()

        # Add external current.
        new_current += self.external_current.value

        # Destabilize if the current has changed.
        if abs(old_current - new_current) > 0.000001:
            self.current = new_current
            self.stable = False

        # If unstable, perform computations.
        if not self.stable:
            # Activate the axons
            # If they are releasing, their synapse should be activated
            # The axons will cascade computation to the synaptic cleft, which
            #     will modify postsynaptic dendrites.
            axons_stable = all([axon.step(soma_voltage) for axon in self.axons])
            self.stable = self.soma.step(new_current) & axons_stable

    @staticmethod
    def create_synapse(presynaptic, postsynaptic, enzyme_concentration=1.0,
            transporter=Transporters.GLUTAMATE, receptor=Receptors.AMPA,
            axon_delay=0, dendrite_strength=0.0015):
        active_molecules = [x for x in set([mol_id for mol_id in \
                transporter.affinities.keys() + receptor.affinities.keys()])]
        synapse = Synapse(
            postsynaptic_id=postsynaptic.neuron_id,
            initial_enzyme_concentration=enzyme_concentration,
            active_molecules=active_molecules)
        axon = synapse.create_axon(
                    transporter=transporter,
                    replenish_rate=0.5,
                    reuptake_rate=0.5,
                    capacity=10.0,
                    delay=axon_delay,
                    spiking = presynaptic.spiking)
        dendrite = synapse.create_dendrite(
                    receptor=receptor,
                    density=0.25,
                    strength=dendrite_strength,
                    environment=presynaptic.environment)

        presynaptic.axons.append(axon)
        presynaptic.synapses.append(synapse)
        postsynaptic.dendrites.append(dendrite)
        return synapse

    @staticmethod
    def create_gap_junction(presynaptic, postsynaptic, conductance):
        presynaptic.gap_junctions.append((postsynaptic,conductance))
        postsynaptic.gap_junctions.append((presynaptic,conductance))
        presynaptic.active_gap_junctions = True
        postsynaptic.active_gap_junctions = True
