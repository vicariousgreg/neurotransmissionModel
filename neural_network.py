# Neural Network
#
# The neural network is a factory used to create subcellular components, full
#     neurons, and neural assemblies.  Components get registered in an
#     environment to aid in synchronizing activity over time steps.

from axon import Axon
from dendrite import Dendrite
from synaptic_cleft import SynapticCleft
from environment import Environment, BatchEnvironment

class NeuralNetwork:
    def __init__(self):
        self.environment = BatchEnvironment()
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

    def create_synaptic_cleft(self, **args):
        return self.build(SynapticCleft, args)

    def create_dendrite(self, **args):
        return self.build(Dendrite, args)
