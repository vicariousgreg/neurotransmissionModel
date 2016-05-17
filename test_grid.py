import argparse
import Image

from plot import plot

from neuron import NeuronTypes
from neuron_factory import NeuronFactory, ConstantDriver

simple_image = [
    [0, 100, 255],
    [255, 100, 0],
    [100, 0, 255],
]

def test_grid(image=simple_image):
    height = len(image)
    width = len(image[0])

    neuron_factory = NeuronFactory()
    neuron_grid = neuron_factory.create_neuron_grid(width, height, base_current=0.0)

    neuron_data = []

    for i in xrange(height):
        for j in xrange(width):
            neuron_factory.register_driver(
                neuron_grid[i][j],
                ConstantDriver(activation=image[i][j]*0.8/255))

    for _ in xrange(args.iterations):
        neuron_data.append(neuron_grid[0][0].soma.get_scaled_voltage())
        neuron_factory.step()
        if len(neuron_factory.tokens) == 0: break

    activity = []
    for row in neuron_grid:
        activity +=  \
            [abs(255.0 * neuron.soma.get_scaled_voltage() / 0.2574)
                for neuron in row]
    print(activity)

    im = Image.new('L', (width, height))
    im.putdata(activity)
    im.save('test.png')

    #if not args.silent:
    #    plot([("neuron", neuron_data)], title="Photoreceptor test")
    #print("Saved %d out of %d cycles." % (neuron_factory.stable, neuron_factory.time))

def main():
    test_grid()

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
    parser.add_argument("-i", "--iterations", type = int, default = 50000, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
