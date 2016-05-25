# Neuron Model

from multiprocessing import Value
from enum import enum
from soma import Soma, SOMA_TYPES
from synapse import SpikingSynapse, GradedSynapse
from receptor import epsp

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

        # Soma
        if neuron_type == NeuronTypes.PHOTORECEPTOR:
            self.soma = Soma(environment=environment,
                soma_type=SOMA_TYPES.PHOTORECEPTOR, record=record, spiking=False)
            self.spiking = False
        elif neuron_type == NeuronTypes.HORIZONTAL:
            base_current = -10
            self.soma = Soma(environment=environment,
                soma_type=SOMA_TYPES.HORIZONTAL, record=record, spiking=False)
            self.spiking = False
        elif neuron_type == NeuronTypes.GANGLION:
            self.soma = Soma(environment=environment,
                soma_type=SOMA_TYPES.DEFAULT, record=record, spiking=True)
            self.spiking = True

        # Synapses
        self.in_synapses = []
        self.out_synapses = []

        # Gap junctions
        self.gap_junctions = []
        self.active_gap_junctions = False

        # Currents
        self.current = base_current
        self.base_current = base_current
        self.ligand_current = 0.0
        self.external_current = Value('d', 0.0)

        # Active flags
        self.stable = False

    def get_record(self, spikes=False):
        if spikes:
            return self.environment.spikes[self.soma.env_id]
        else:
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
        for synapse in self.in_synapses:
            synapse.activate_dendrites(self)
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

        for synapse in self.out_synapses:
            synapse.step(soma_voltage)
        self.soma.step(new_current)

        '''
        # Destabilize if the current has changed.
        if abs(old_current - new_current) > 0.000001:
            self.current = new_current
            self.stable = False

        # If unstable, perform computations.
        if not self.stable:
            # Activate the output synapses
            all([synapse.step(soma_voltage) for synapse in self.out_synapses])
            # Activate the soma
            self.stable = self.soma.step(new_current)
        '''

    @staticmethod
    def create_synapse(pre, post, receptor=epsp, delay=0, strength=1):
        if pre.spiking:
            synapse = SpikingSynapse(receptor, delay, strength, pre.environment)
        else:
            synapse = GradedSynapse(receptor, delay, strength, pre.environment)

        pre.out_synapses.append(synapse)
        post.in_synapses.append(synapse)
        return synapse

    @staticmethod
    def create_gap_junction(pre, post, conductance):
        pre.gap_junctions.append((post,conductance))
        post.gap_junctions.append((pre,conductance))
        pre.active_gap_junctions = True
        post.active_gap_junctions = True
