import argparse
from random import random

from plot import plot, draw

from molecule import Transporters, Receptors
from neuron import NeuronTypes
from neuron_factory import NeuronFactory
from tools import ConstantDriver

import matplotlib.image as mpimg

#img = mpimg.imread('../_static/stinkbug.png')
#lum_img = img[:,:,0]
#imgplot = plt.imshow(lum_img)

simple_image = [
    [0, 100, 255],
    [255, 100, 0],
    [100, 0, 255],
]
width = 10
height = 10
random_image = [[random() * 255 for _ in xrange(width)] for __ in xrange(height)]
graded_image = [[10*i for i in xrange(width)] for __ in xrange(height)]
dark_image = [[0 for _ in xrange(width)] for __ in xrange(height)]
light_image = [[255 for _ in xrange(width)] for __ in xrange(height)]

def test_grid(
        #image=random_image):
        image=graded_image):
        #image=light_image):
        #image=dark_image):
    height = len(image)
    width = len(image[0])

    neuron_factory = NeuronFactory(num_threads=1)
    photoreceptor_grid = neuron_factory.create_neuron_grid(width, height,
                        neuron_type=NeuronTypes.PHOTORECEPTOR, record=True)
    ganglion_grid = neuron_factory.create_neuron_grid(width, height, record=True)

    neuron_data = []

    # Create drivers and Connect ganglion cells.
    for i in xrange(height):
        print(image[i])
        for j in xrange(width):
            neuron_factory.create_synapse(photoreceptor_grid[i][j], ganglion_grid[i][j],
                dendrite_strength=100)
            neuron_factory.register_driver(
                photoreceptor_grid[i][j],
                ConstantDriver(current=-image[i][j], delay=10))

    for _ in xrange(args.iterations):
        neuron_factory.step()
    neuron_factory.close()

    photo_activity = []
    for row in photoreceptor_grid:
        d = [neuron.get_record()[-1] for neuron in row]
        photo_activity.append(d)
        #print(d)

    ganglion_activity = []
    for row in ganglion_grid:
        d = [len(tuple(x for x in neuron.get_record() if x > 30.0)) for neuron in row]
        #print([x for x in row[0].get_record()])
        ganglion_activity.append(d)
        #print(d)

    draw((image, photo_activity, ganglion_activity), ("Input", "Photoreceptors", "Ganglion"))
    #draw((image, photo_activity), ("Input", "Photoreceptors"))
    #draw((image,), ("Input",))

    '''
    data = []
    for i in xrange(height):
        for j in xrange(width):
            data.append(("%d %d" % (i,j), photoreceptor_grid[i][j].get_record()))
    if not args.silent:
        plot(data, title="Photoreceptor test")
    '''

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
    parser.add_argument("-i", "--iterations", type = int, default = 100, help = 
    """table""")

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
