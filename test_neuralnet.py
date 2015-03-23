import unittest
from neuralnet import *


class TestNeuron(unittest.TestCase):

    # a neuron has dendrites and an axon
    def test___init__(self):
        pass

    # a neuron attaches downstream to another neuron
    def test_attach_my_axon(self):

        n1 = Neuron()
        n2 = Neuron()

        n1.attach_my_axon(n2)

        # n1's axon should point to n2
        self.assertTrue(n1.axon == n2)

        # n2's dendrite tree should include n1
        self.assertTrue(n2.dendrite_tree.__contains__(n1))

    def test_attach_my_dendrite(self):

        n1 = Neuron()
        n2 = Neuron()

        n2.attach_my_dendrite(n1)

        # n2's dendrite tree should include n1
        self.assertTrue(n2.dendrite_tree.__contains__(n1))
