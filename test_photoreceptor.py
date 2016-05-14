import argparse

from plot import plot

from synapse import Synapse
from neuron import Neuron, NeuronTypes
from environment import NeuronEnvironment

def test_photoreceptor(
        #spike_strengths=[0.5]):
        spike_strengths=[0.1, 0.5, 0.7]):
    data = []
    period = 7000
    frequency = 12000

    current_data = []
    current = 0.0

    for i in xrange(5000):
        current_data.append(-0.5)
    for i in xrange(30000):
        if i % frequency == 0:
            current = -0.4
        elif i % frequency == period:
            current = -0.5
        current_data.append(current)

    data.append(("current", current_data))

    for strength in spike_strengths:
        environment = NeuronEnvironment()
        neuron = Neuron(neuron_type=NeuronTypes.PHOTORECEPTOR, environment=environment)
        post = Neuron(environment=environment)
        synapse = Neuron.create_synapse(neuron, post)
        axon = neuron.axons[0]
        dendrite = post.dendrites[0]
        synapse.set_enzyme_concentration(0.5)

        cleft_data = []
        dendrite_data = []

        m=0.0
        for i in xrange(5000):
            neuron.step(m, resolution=100)
            synapse.step(i)
            environment.step()

            cleft_data.append(synapse.synaptic_cleft.get_concentration())
            dendrite_data.append(dendrite.get_concentration())
        for i in xrange(30000):
            if i % frequency == 0:
                m = strength
            elif i % frequency == period:
                m = 0.0

            neuron.step(m, resolution=100)
            environment.step()
            synapse.step(i)

            cleft_data.append(synapse.synaptic_cleft.get_concentration())
            dendrite_data.append(dendrite.get_concentration())

        data.append(neuron.soma.get_data("Photoreceptor %f" % strength))
        #data.append(axon.get_data())
        data.append(("dendrite %f" % strength, dendrite_data))
        #data.append(("synaptic cleft", cleft_data))
    if not args.silent:
        plot(data, title="Photoreceptor test")

def main():
    test_photoreceptor()

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

    return parser.parse_args()

if __name__ == "__main__":
    args = set_options()
    main()
