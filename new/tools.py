# Drivers can be added to activate particular neurons at each timestep.
# 
# Probes can be added to any component to take measurements of voltage, current,
#     or concentration over the course of the simulation.

from multiprocessing import Manager
manager = Manager()

class ConstantDriver:
    def __init__(self, activation=0.0, delay=0):
        self.activation = activation
        self.delay = delay
        if delay > 0: self.drive = self.predelay
        else: self.drive = self.postdelay

    def predelay(self, neuron, time):
        if time-self.delay >= 0:
            self.drive = self.postdelay
            neuron.set_external_current(self.activation)

    def postdelay(self, neuron, time):
        pass

class PulseDriver:
    def __init__(self, current=0.0, period=1000, length=500,
                        delay=0, record=False):
        self.current = current
        self.period = period
        self.length = length
        self.delay = delay
        self.record = record
        self.data = []

    def drive(self, neuron, time):
        time -= self.delay
        if time >= 0 and time % self.period == 0:
            neuron.set_external_current(self.current)
            if self.record: self.data.append(-0.2)
        elif time % self.period == self.length:
            neuron.set_external_current(0.0)
            if self.record: self.data.append(-0.3)

class Probe:
    def __init__(self):
        self.data = manager.list()
        self.last_reading = None
        self.length = 0

    def record(self, reading, time):
        data = [self.last_reading] * (time - self.length)
        self.last_reading = reading
        data.append(reading)
        self.data.append(data)
