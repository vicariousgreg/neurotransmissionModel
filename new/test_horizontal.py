import argparse

from plot import plot

from neuron import Neuron
from soma import Soma
from neuron_factory import NeuronFactory
from neuron import NeuronTypes
from tools import ConstantDriver
from molecule import Transporters, Receptors

def transmit(strengths=[-255, -100, -50, -10, 0]):
    data = []
    neuron_factory = NeuronFactory()
    dendrite_strength = 100
    if args.silent:
        photoreceptor = neuron_factory.create_neuron(neuron_type=NeuronTypes.PHOTORECEPTOR)
        horizontal = neuron_factory.create_neuron(neuron_type=NeuronTypes.HORIZONTAL)
        synapse = neuron_factory.create_synapse(photoreceptor, horizontal,
            dendrite_strength=dendrite_strength)
    else:
        photoreceptor = neuron_factory.create_neuron(neuron_type=NeuronTypes.PHOTORECEPTOR, record=True)
        horizontal = neuron_factory.create_neuron(neuron_type=NeuronTypes.HORIZONTAL, record=True)
        synapse = neuron_factory.create_synapse(photoreceptor, horizontal,
            dendrite_strength=dendrite_strength)
        synapse = neuron_factory.create_synapse(horizontal, photoreceptor,
            transporter=Transporters.GABA, receptor=Receptors.GABA,
            dendrite_strength=dendrite_strength)

    for strength in strengths:
        driver = ConstantDriver(current=strength, delay=100)
        neuron_factory.register_driver(photoreceptor, driver)
        neuron_factory.step(args.iterations)

    #print("Saved %d out of %d cycles." % (neuron_factory.stable_count, neuron_factory.time))

    if not args.silent:
        data.append(("Photoreceptor", photoreceptor.get_record()))
        data.append(("Horizontal Cell", horizontal.get_record()))
        plot(data, title="Horizontal Cell Test")

def main():
    #transmit(strength = -0.5)
    transmit()
    #transmit(strength = 0.1)

def set_options():
    """
    Retrieve the user-entered arguments for the program.
    """
    parser = argparse.ArgumentParser(description = 
    """Tests basic neurotransmission from axon->synaptic cleft->dendrite.""")
    parser.add_argument("-v", "--verbose", action = "store_true", help = 
    """print table""")
    parser.add_argument("-s", "--silent", action = "store_true", help = 
    """do not display graphs""")
    parser.add_argument("-i", "--iterations", type = int, default = 1000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
