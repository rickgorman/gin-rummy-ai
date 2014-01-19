#!/usr/bin/python
#
# neuralnet.py
#
# 2014/01/18
# rg
#
# base neural networking classes


class Node:
    def __init__(self):
        self.value = 0
        self.children = []


class Layer:
    # instantiate a new Layer with a given number of nodes
    def __init__(self, node_count=20):
        self.nodes = []
        for _ in range(node_count):
            self.nodes.append(Node())


class MultiInputSingleHiddenSingleOutputNeuralNet:
    hidden_layer_size = 100

    def __init__(self, num_inputs=10, num_outputs=10):
        self.input_layer  = Layer(num_inputs)
        self.hidden_layer = Layer(self.hidden_layer_size)
        self.output = None





