import argparse

from plot import plot

from neuron import NeuronTypes
from neuron_factory import NeuronFactory
from tools import PulseDriver

def test_photoreceptor(
        print_axon=True,
        print_postsynaptic=True,
        print_photoreceptor=True,
        print_dendrite=False,
        print_synaptic_cleft=False,
        spike_strengths=[-100]):

    data = []
    length = 60
    period = 100
    rest_length = 50

    for strength in spike_strengths:
        neuron_factory = NeuronFactory()
        photoreceptor = neuron_factory.create_neuron(
            neuron_type=NeuronTypes.PHOTORECEPTOR,
            record = True)
        post = neuron_factory.create_neuron(record = True)

        synapse = neuron_factory.create_synapse(photoreceptor, post, dendrite_strength=50)
        synapse.set_enzyme_concentration(0.5)

        driver_name = "Light activation %f" % strength
        neuron_factory.register_driver(photoreceptor,
            PulseDriver(current=strength, period=period,
                length=length, delay=rest_length, record=True),
            name = driver_name)
        neuron_factory.step(args.iterations)

        if print_photoreceptor: data.append(("Photoreceptor", photoreceptor.get_record()))
        if print_postsynaptic: data.append(("Post", post.get_record()))
    data.append(neuron_factory.get_driver_data(driver_name))
    if not args.silent:
        plot(data, title="Photoreceptor test")

def main():
    test_photoreceptor(
        print_axon=True,
        print_postsynaptic=True,
        print_photoreceptor=True,
        print_dendrite=False,
        print_synaptic_cleft=False,
        spike_strengths=[-100])

    test_photoreceptor(
        print_axon=False,
        print_postsynaptic=True,
        print_photoreceptor=True,
        print_dendrite=False,
        print_synaptic_cleft=False,
        spike_strengths=[-10, -100])

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
    parser.add_argument("-i", "--iterations", type = int, default = 250, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
