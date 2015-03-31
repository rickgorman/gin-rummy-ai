#!/usr/bin/python
#
# neuralnet.py
#
# 2014/01/18
# rg
#
# base neural networking classes

from math import exp
from utility import indent_print

# TODO: we need to punish a network for doing something bad, i.e discarding at 10 cards or drawing at 11 cards.


class NeuralNet(object):
    # take in an array of sensors, a dict of lists of weights (weights[input]=[0.1,0.2,...]) and an array of output_keys
    def __init__(self, sensors, weights, output_keys):
        assert len(sensors) > 0, 'must have at least one sensor'
        assert len(weights) > 0, 'must have non-empty weights dict'
        assert len(output_keys) > 0, 'must have at least one output_key'

#        self.validate_weights()

        self.sensors = sensors
        self.weights = weights
        self.output_keys = output_keys

        self.input_layer = []
        self.hidden_layer = []
        self.output_layer = []

        self.create_input_layer()
#        self.create_hidden_layer()
#        self.create_output_layer()

    def validate_weights(self):
        # ensure we have an input, hidden and output key
        assert 'input'  in self.weights, "no input  weights"
        assert 'hidden' in self.weights, "no hidden weights"
        assert 'output' in self.weights, "no output weights"

        # ensure we have exactly one input weight per sensor buffer item
        expected_input_count = 0
        for sensor in self.sensors:
            for _ in sensor.buffer.keys():
                expected_input_count += 1
        assert len(self.weights['input']) == expected_input_count, "input weight mismatch"

        # ensure we have exactly one hidden list per hidden
        assert self.calculate_hidden_count() == len(self.weights['hidden']), "hidden weight key mismatch"

        # ensure each hidden list has length equal to number of input neurons
        for i in range(self.calculate_hidden_count()):
            assert len(self.weights['hidden'][i]) == expected_input_count, "hidden weight count mismatch"

        # ensure we have exactly one output list per output
        assert len(self.output_keys) == len(self.weights['output']), "output weight key mismatch"

        # ensure each output list has length equal to number of hidden neurons
        for i in range(len(self.output_keys)):
            assert len(self.weights['output'][i]) == self.calculate_hidden_count(), "output weight count mismatch"

        # as long as we made it this far, we're good
        return True

    def calculate_hidden_count(self):
        return int((len(self.input_layer) + len(self.output_keys)) * 2/3)

    def create_input_layer(self):
        for sensor in self.sensors:
            for key in sensor.buffer.keys():
                # take advantage of the buffer key indexing (0, 1, ...) to match up with the appropriate weight
                weight = self.weights['input'][key]
                # create a uniqueish id
                myid = sensor.__class__.__name__ + '-' + str(sensor.id) + '-' + str(key)
                self.input_layer.append(InputPerceptron(sensor, weight=weight, myid=myid, index=key))

    # create hidden neurons and attach them to each of our input neurons using the weights in weights['hidden']
    def create_hidden_layer(self):
        count = self.calculate_hidden_count()
        for i in range(count):
            hp = HiddenPerceptron(self.input_layer, self.weights['hidden'][i])
            self.hidden_layer.append(hp)


class Perceptron(object):
    def __init__(self, myid=None):
        self.inputs = {}
        if None == myid:
            self.id = self.__repr__()
        else:
            self.id = myid

    # uplink to an upstream perceptron, storing the connection's weight in a dict
    def add_input(self, target, weight):
        self.inputs[target] = weight

    # aggregate input weights
    def step_function(self):
        return sum(self.inputs.values())

    @staticmethod
    def sigmoid(num):
        return 1 / (1 + exp(-num))

    # return the sigmoid of: the sum of our inputs multiplied by their respective weights
    def generate_output(self, indent_level=0):
        func_debug = 0
        weighted = 0
        sigmoided = 0

        if func_debug:
            indent_print(indent_level, "running generate_output() for: " + self.id)

        for each_input in self.inputs.keys():
            output = each_input.generate_output(indent_level=indent_level+1)
            weighted += self.inputs[each_input] * output
            sigmoided = Perceptron.sigmoid(weighted)
            # debug output
            if func_debug:
                indent_print(indent_level+1, "looking at connection from " + each_input.id + " to " + self.id)
                indent_print(indent_level+2, "input weight: " + str(self.inputs[each_input]))
                indent_print(indent_level+2, "output: " + str(output))
                indent_print(indent_level+2, "weighted: " + str(weighted))
                indent_print(indent_level+2, "sigmoided: " + str(round(sigmoided, 4)))

        return sigmoided


class InputPerceptron(Perceptron):
    def __init__(self, environment_sensor, weight=None, myid=None, index=None):
        self.sensor = environment_sensor
        if index is None:
            raise AssertionError("no index supplied")
        else:
            self.index = index

        if weight is None:
            raise AssertionError("no weight supplied")
        else:
            self.weight = weight

        Perceptron.__init__(self, myid)

    def generate_output(self, indent_level=0):
        func_debug = 0

        # ask the sensor for its current sense of the world, weight it, and then run it through the sigmoid function
        sigmoided = Perceptron.sigmoid(self.sense() * self.weight)

        if func_debug:
            indent_print(indent_level, "running generate_output() for: " + self.id)
            indent_print(indent_level+1, "sigmoid(" + self.id + ".sense()) = " + str(round(sigmoided, 4)))

        return sigmoided

    # probe the sensor
    def sense(self):
        return self.sensor.get_value_by_index(self.index)


class MultiInputPerceptron(Perceptron):
    def __init__(self, input_neurons, neuron_weights, myid=None):
        assert len(input_neurons) == len(neuron_weights), "must have equal number of neurons and weights"
        super(MultiInputPerceptron, self).__init__(myid=myid)

        # connect to each input neuron
        for i in range(len(input_neurons)):
            self.add_input(input_neurons[i], neuron_weights[i])


class HiddenPerceptron(MultiInputPerceptron):
    pass