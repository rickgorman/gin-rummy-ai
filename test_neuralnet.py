import unittest
from neuralnet import *
from observer import *
from ginplayer import *


# noinspection PyMissingConstructor
class MockSensor(Observer):
    def __init__(self, obj):
        super(MockSensor, self).__init__(obj)
        self.buffer = [obj.value]

    def sense(self):
        return self.target.value


class MockObservable(Observable):
    def __init__(self, val):
        self.value = val
        super(MockObservable, self).__init__()


class TestPerceptron(unittest.TestCase):

    def setUp(self):
        self.p1 = Perceptron(myid='self.p1')
        self.p2 = Perceptron(myid='self.p2')
        self.weight = 0.5

    def test___init__(self):
        # a perceptron stores a dict of input Perceptrons along with the respective weights to each
        self.assertIsInstance(self.p1.inputs, dict)

    def test_add_input(self):
        # ensure we can only add each input once
        self.p1.add_input(self.p2, self.weight)
        self.p1.add_input(self.p2, self.weight)
        self.assertEqual(1, len(self.p1.inputs))

    def test_step_function(self):
        p3 = Perceptron()

        # we're using the sigmoid function, so we expect a result in [0,1] -- inclusive due to rounding.
        # add a bunch of positive weight and ensure they're being summed prior to hitting the sigmoid by verifying
        # the sigmoid grows after each add.

        lastval = 0
        for i in range(20):
            p = Perceptron()
            p3.add_input(p, self.weight)
            val = p3.step_function()
            self.assertTrue(val > lastval)
            lastval = val

        # do the same thing, but with negative weights
        for i in range(20):
            p = Perceptron()
            p3.add_input(p, -self.weight)
            val = p3.step_function()
            self.assertTrue(val < lastval)
            lastval = val

    def test_sigmoid(self):
        # input/output values for the sigmoid function
        reference = {0:   0.5,
                     1:   0.731058578,
                     10:  0.999954602,
                     -1:  0.268941421,
                     -10: 0.000045397}

        for key in reference.keys():
            self.assertAlmostEqual(self.p1.sigmoid(key), reference[key], 4)

    def test_generate_output(self):
        # we'll set up a simple neural net with layers as follows:
        # - input layer: 2 neurons
        # - hidden layer: 2 neurons
        # - output layer: 1 neuron
        # we'll verify that the output value matches a hand-calculated value

        mo1_val = 5
        mo2_val = 8

        ms1 = MockSensor(MockObservable(mo1_val))
        ms2 = MockSensor(MockObservable(mo2_val))

        input1 = InputPerceptron(ms1, myid='input1', index=0)
        input2 = InputPerceptron(ms2, myid='input2', index=0)
        hidden1 = Perceptron(myid='hidden1')
        hidden2 = Perceptron(myid='hidden2')
        output1 = Perceptron(myid='output1')

        # arbitrary weights
        i1_h1_weight = 0.3
        i1_h2_weight = 0.4
        i2_h1_weight = 0.5
        i2_h2_weight = 0.6
        h1_o1_weight = 0.1
        h2_o1_weight = 0.2

        # link weights up to inputs
        output1.add_input(hidden1, h1_o1_weight)
        output1.add_input(hidden2, h2_o1_weight)
        hidden1.add_input(input1, i1_h1_weight)
        hidden1.add_input(input2, i1_h2_weight)
        hidden2.add_input(input1, i2_h1_weight)
        hidden2.add_input(input2, i2_h2_weight)

        # calculate this by hand. did on paper as well, same value of 0.5539 for weights given on 2015/03/23 commit
        h1_step = Perceptron.sigmoid(Perceptron.sigmoid(mo1_val)*i1_h1_weight +
                                     Perceptron.sigmoid(mo2_val)*i2_h1_weight)
        h2_step = Perceptron.sigmoid(Perceptron.sigmoid(mo1_val)*i1_h2_weight +
                                     Perceptron.sigmoid(mo2_val)*i2_h2_weight)
        expected = Perceptron.sigmoid(h1_step*h1_o1_weight + h2_step*h2_o1_weight)

        generated = output1.generate_output()
        self.assertAlmostEqual(expected, generated, 3)


# noinspection PyProtectedMember
class TestInputPerceptron(unittest.TestCase):
    def setUp(self):
        self.c = GinCard(5, 'd')
        self.p = GinPlayer()
        self.sensor = PlayerObserver(self.p)
        self.ip = InputPerceptron(self.sensor, myid='self.ip', index=0)

    def test__init__(self):
        # ensure we store our sensor
        self.assertEqual(self.ip.sensor, self.sensor)
        self.assertIsInstance(self.ip.sensor, Observer)

    def test_sense(self):
        # ensure we sense an input properly
        self.p._add_card(self.c)
        self.assertEqual(self.ip.sense(), self.p.hand.cards[self.ip.index].ranking())

    def test_generate_output(self):
        # ensure we output the sigmoided sense
        self.p._add_card(self.c)
        self.assertEqual(Perceptron.sigmoid(self.p.hand.cards[self.ip.index].ranking()), self.ip.generate_output())
