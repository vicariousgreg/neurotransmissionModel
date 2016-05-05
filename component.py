# Component
#
# Components are neural components that run through timesteps during the
#     simulation.

class Component(object):
    def __init__(self): pass

    def step(self, time):
        raise ValueError("Cannot simulate abstract class!")
