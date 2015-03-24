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

# Notes:
# - we need to punish a network for doing something bad, i.e discarding at 10 cards or drawing at 11 cards.


class Perceptron(object):
    def __init__(self, myid=None):
        self.inputs = {}
        if None == myid:
            self.id = self.__repr__()
        else:
            self.id = myid

    # connect this perceptron to those upstream of it
    def attach_one_input(self, target):
        target.attach_my_dendrite(self)

    # uplink to an upstream perceptron
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
        multiplied = 0
        indent_print(indent_level, "running generate_output() for: " + self.id)
        for each_input in self.inputs.keys():
            output = each_input.generate_output(indent_level=indent_level+1)
            multiplied += self.inputs[each_input] * output
            sigmoided = Perceptron.sigmoid(multiplied)
            indent_print(indent_level+1, "looking at connection from " + each_input.id + " to " + self.id)
            indent_print(indent_level+2, "input weight: " + str(self.inputs[each_input]))
            indent_print(indent_level+2, "output: " + str(output))
            indent_print(indent_level+2, "multiplied: " + str(multiplied))
            indent_print(indent_level+2, "sigmoided: " + str(round(sigmoided, 4)))

        return sigmoided


class InputPerceptron(Perceptron):
    def __init__(self, environment_sensor, myid=None):
        self.sensor = environment_sensor
        Perceptron.__init__(self, myid)

    def generate_output(self, indent_level=0):
        sensed = self.sensor.sense()
        sigmoided = Perceptron.sigmoid(sensed)
        indent_print(indent_level, "running generate_output() for: " + self.id)
        indent_print(indent_level+1, "sigmoid(" + self.id + ".sense()) = " + str(round(sigmoided, 4)))
        return sigmoided