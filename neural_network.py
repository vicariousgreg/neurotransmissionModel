# Neural Network
#
# The neural network is a factory used to create subcellular components, full
#     neurons, and neural assemblies.  Components get assigned an identifier to
#     aid in synchronizing activity over time steps.
#
# Neural Networks hold buffers for neurotransmitter concentration.
# Computations are performed on the previous timestep's concentrations

from axon import Axon
from dendrite import Dendrite
from synapse import Synapse
from environment import Environment

class NeuralNetwork:
    def __init__(self):
        self.environment = Environment()
        self.components = []

    def step(self, time):
        self.environment.step(time)
        for component in self.components:
            component.step(time)

    def build(self, constructor, args):
        args["environment"] = self.environment
        component =  constructor(**args)
        self.components.append(component)
        return component

    def create_axon(self, **args):
        return self.build(Axon, args)

    def create_synapse(self, **args):
        return self.build(Synapse, args)

    def create_dendrite(self, **args):
        return self.build(Dendrite, args)

def test():
    nn = NeuralNetwork()
    components = nn.create_axon(),nn.create_synapse(),nn.create_dendrite()

    tuple(component.set_concentration(0.5) for component in components)
    for time in xrange(5):
        print("\n" + str(time))
        nn.step(time)

        print(tuple(component.get_concentration() for component in components))
        print(nn.environment.prev_concentrations)
