import argparse

from plot import plot

from neuron import Neuron
from soma import Soma
from neuron_factory import NeuronFactory
from neuron import NeuronTypes
from tools import ConstantDriver
from receptor import Receptors

def horizontal(strengths=[-255, -100, -50, -10, 0]):
    data = []
    neuron_factory = NeuronFactory()
    dendrite_strength = 10

    photoreceptor1 = neuron_factory.create_neuron(neuron_type=NeuronTypes.PHOTORECEPTOR, record=True)
    photoreceptor2 = neuron_factory.create_neuron(neuron_type=NeuronTypes.PHOTORECEPTOR, record=True)
    horizontal = neuron_factory.create_neuron(neuron_type=NeuronTypes.HORIZONTAL, record=True)
    synapse = neuron_factory.create_synapse(photoreceptor1, horizontal,
        dendrite_strength=dendrite_strength)
    synapse = neuron_factory.create_synapse(horizontal, photoreceptor1,
        receptor=Receptors.GABA, dendrite_strength=dendrite_strength*5)

    synapse = neuron_factory.create_synapse(photoreceptor2, horizontal,
        dendrite_strength=dendrite_strength)
    synapse = neuron_factory.create_synapse(horizontal, photoreceptor2,
        receptor=Receptors.GABA, dendrite_strength=dendrite_strength*5)

    #driver = ConstantDriver(current=-255, delay=100)
    #neuron_factory.register_driver(photoreceptor2, driver)
    for strength in strengths:
        driver = ConstantDriver(current=strength, delay=100)
        neuron_factory.register_driver(photoreceptor1, driver)
        neuron_factory.step(args.iterations)
        driver = ConstantDriver(current=strength/2, delay=100)
        neuron_factory.register_driver(photoreceptor2, driver)
        neuron_factory.step(args.iterations)

    #print("Saved %d out of %d cycles." % (neuron_factory.stable_count, neuron_factory.time))

    if not args.silent:
        data.append(("Photoreceptor (variable)", photoreceptor1.get_record()))
        data.append(("Photoreceptor (stable)", photoreceptor2.get_record()))
        data.append(("Horizontal Cell", horizontal.get_record()))
        plot(data, title="Horizontal Cell Test")

def main():
    #horizontal(strength = -0.5)
    horizontal()
    #horizontal(strength = 0.1)

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
