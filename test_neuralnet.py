import unittest
from neuralnet import *
from observer import *
from ginplayer import *
from gintable import *


# noinspection PyMissingConstructor
class MockSensor(Observer):
    def __init__(self, obj):
        super(MockSensor, self).__init__(obj)
        self.buffer = [obj.value]

    # def sense(self):
    #     return self.target.value


class MockObservable(Observable):
    def __init__(self, val):
        self.value = val
        super(MockObservable, self).__init__()

    def organize_data(self):
        pass


class MockNeuralNetwork(object):
    def __init__(self, action, index, accept_improper_knock):
        self.outputs = {'action': action, 'index': index, 'accept_improper_knock': accept_improper_knock}

    def pulse(self):
        pass


# noinspection PyDictCreation
class TestNeuralNet(unittest.TestCase):

    @staticmethod
    def clear_all_layers(nn):
        assert isinstance(nn, NeuralNet)
        nn.input_layer = []
        nn.hidden_layer = []
        nn.output_layer = []

    def setUp(self):
        self.p = GinPlayer()
        self.t = GinTable()
        self.p.table = self.t
        for _ in range(11):
            self.p.draw()
        self.pobs = PlayerObserver(self.p)

        self.sensors = [self.pobs]
        self.output_keys = ['action', 'index', 'accept-improper-knock']
        self.weights = {'input': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.97],
                        'hidden': [],
                        'output': []}
        # set up the same set of weights for each hidden neuron (9 neurons, 11 weights per neuron)
        for _ in range(9):
            self.weights['hidden'].append([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.96, 0.97])

        # set up the same set of weights for each output neuron (3 neurons, 9 weights per neuron)
        for _ in range(3):
            self.weights['output'].append([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

    def test___init__(self):
        invalid_weights = {'input': [0.5], 'output': []}
        # require at least one sensor, one weight and one output
        self.assertRaises(AssertionError, NeuralNet, [], invalid_weights, self.output_keys)
        self.assertRaises(AssertionError, NeuralNet, self.sensors, {}, self.output_keys)
        self.assertRaises(AssertionError, NeuralNet, self.sensors, invalid_weights, [])

    def test_validate_weights(self):
        self.nn = NeuralNet(self.sensors, self.weights, self.output_keys)
        self.assertTrue(self.nn.validate_weights())

        # remove an input weight
        self.weights['input'].pop()
        self.assertRaises(AssertionError, self.nn.validate_weights)

        # add it back, remove a whole hidden neuron of weights
        self.weights['input'].append(0.97)
        self.assertTrue(self.nn.validate_weights())
        borrow = self.weights['hidden'].pop()
        self.assertRaises(AssertionError, self.nn.validate_weights)

        # add it back, remove a single weight from one hidden
        self.weights['hidden'].append(borrow)
        self.assertTrue(self.nn.validate_weights())
        borrow = self.weights['hidden'][0].pop()
        self.assertRaises(AssertionError, self.nn.validate_weights)

        # add it back, remove the entire output list
        self.weights['hidden'][0].append(borrow)
        self.assertTrue(self.nn.validate_weights())
        borrow = self.weights.pop('output', None)
        self.assertRaises(AssertionError, self.nn.validate_weights)

        # add it back, remove a single weight from one output neuron
        self.weights['output'] = borrow
        self.assertTrue(self.nn.validate_weights())
        self.weights['output'][0].pop()
        with self.assertRaises(AssertionError):
            self.nn.validate_weights()

    def test_calculate_hidden_count(self):
        # one example should be good enough to test the math
        self.nn = NeuralNet(self.sensors, self.weights, self.output_keys)
        self.assertEqual(9, self.nn.calculate_hidden_count())

    def test_create_input_layer(self):
        self.nn = NeuralNet(self.sensors, self.weights, self.output_keys)
        # wipe the input_layer and ensure it has been recreated with the correct number of input neurons
        TestNeuralNet.clear_all_layers(self.nn)
        self.nn.create_input_layer()
        self.assertEqual(len(self.nn.input_layer), sum([len(s.buffer.keys()) for s in self.sensors]))

    def test_create_hidden_layer(self):
        self.test_create_input_layer()
        self.nn.create_hidden_layer()
        # make sure we have the right number of hidden neurons
        self.assertEqual(len(self.nn.hidden_layer), int((len(self.nn.input_layer) + len(self.output_keys)) * 2/3))

        # ensure that each hidden neuron has each input neuron in its inputs
        for hn in self.nn.hidden_layer:
            found = {}
            for n in hn.inputs.keys():
                found[n] = True
            self.assertEqual(len(found), len(self.pobs.buffer))

    def test_create_output_layer(self):
        self.test_create_hidden_layer()
        self.nn.create_output_layer()
        self.assertEqual(len(self.nn.output_layer), len(self.output_keys))

        # ensure that each output neuron has each hidden neuron in its inputs
        for o in self.nn.output_layer:
            found = {}

            output_key = o.keys()[0]
            output_neuron = o[output_key]

            for input_neuron in output_neuron.inputs.keys():
                found[input_neuron] = True
            self.assertEqual(len(found), len(self.nn.hidden_layer))

    def test_pulse(self):
        # create invalid values for outputs
        self.test_create_output_layer()
        for key in self.output_keys:
            self.nn.outputs[key] = -1

        # change the first input weight of each output neuron to make each final output value unique
        new_values = [0.02, 0.08, 0.55]
        for item in self.nn.output_layer:
            neuron = item[item.keys()[0]]
            first_input = neuron.inputs.keys()[0]
            neuron.inputs[first_input] = new_values.pop()

        self.nn.pulse()

        found_outputs = {}
        for key in self.nn.outputs:
            # ensure we don't have duplicate outputs
            value = self.nn.outputs[key]
            if value in found_outputs.keys():
                self.fail()
            found_outputs[str(value)] = True

            # ensure our output buffers have new values in (0, 1)
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)


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
        reference = {0: 0.5,
                     1: 0.731058578,
                     10: 0.999954602,
                     -1: 0.268941421,
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

        # arbitrary weights
        i1_weight = 1       # the by-hand calculations below rely on a weight of 1.0 for inputs.
        i2_weight = 1       # TODO: add the sensor-input weight into the by-hand calculations
        i1_h1_weight = 0.3
        i1_h2_weight = 0.4
        i2_h1_weight = 0.5
        i2_h2_weight = 0.6
        h1_o1_weight = 0.1
        h2_o1_weight = 0.2

        input1 = InputPerceptron(ms1, i1_weight, myid='input1', index=0)
        input2 = InputPerceptron(ms2, i2_weight, myid='input2', index=0)
        hidden1 = Perceptron(myid='hidden1')
        hidden2 = Perceptron(myid='hidden2')
        output1 = Perceptron(myid='output1')

        # link weights up to inputs
        output1.add_input(hidden1, h1_o1_weight)
        output1.add_input(hidden2, h2_o1_weight)
        hidden1.add_input(input1, i1_h1_weight)
        hidden1.add_input(input2, i1_h2_weight)
        hidden2.add_input(input1, i2_h1_weight)
        hidden2.add_input(input2, i2_h2_weight)

        # calculate this by hand. did on paper as well, same value of 0.5539 for weights given on 2015/03/23 commit
        h1_step = Perceptron.sigmoid(Perceptron.sigmoid(mo1_val) * i1_h1_weight +
                                     Perceptron.sigmoid(mo2_val) * i2_h1_weight)
        h2_step = Perceptron.sigmoid(Perceptron.sigmoid(mo1_val) * i1_h2_weight +
                                     Perceptron.sigmoid(mo2_val) * i2_h2_weight)
        expected = Perceptron.sigmoid(h1_step * h1_o1_weight + h2_step * h2_o1_weight)

        generated = output1.generate_output()
        self.assertAlmostEqual(expected, generated, 3)


# noinspection PyProtectedMember
class TestInputPerceptron(unittest.TestCase):
    def setUp(self):
        self.c = GinCard(5, 'd')
        self.p = GinPlayer()
        self.sensor = PlayerObserver(self.p)
        self.weight = 0.2
        self.ip = InputPerceptron(self.sensor, weight=self.weight, myid='self.ip', index=0)

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
        expected = Perceptron.sigmoid(self.p.hand.cards[self.ip.index].ranking() * self.weight)
        self.assertEqual(expected, self.ip.generate_output())


# noinspection PyTypeChecker
class TestMultiInputPerceptron(unittest.TestCase):
    def setUp(self):
        self.p = GinPlayer()
        self.sensor = PlayerObserver(self.p)
        self.neuron_weights = [0.5, 0.3]
        self.ip1 = InputPerceptron(self.sensor, weight=self.neuron_weights[0], myid='self.ip1', index=0)
        self.ip2 = InputPerceptron(self.sensor, weight=self.neuron_weights[1], myid='self.ip2', index=1)
        self.inputs = [self.ip1, self.ip2]

    def test___init__(self):
        # ensure that both self.ip1 and self.ip2 are in our inputs
        self.mip = MultiInputPerceptron(self.inputs, self.neuron_weights)
        self.assertIn(self.ip1, self.mip.inputs)
        self.assertIn(self.ip2, self.mip.inputs)

        # ensure that we require equal numbers of inputs and weights
        with self.assertRaises(AssertionError):
            MultiInputPerceptron([self.ip1], ())


class TestOutputPerceptron(unittest.TestCase):
    def setUp(self):
        self.p = GinPlayer()
        self.sensor = PlayerObserver(self.p)
        self.neuron_weights = [0.5]
        self.ip1 = InputPerceptron(self.sensor, weight=self.neuron_weights[0], myid='self.ip1', index=0)
        self.inputs = [self.ip1]

    def test___init__(self):
        # ensure our key gets stored
        output_key = 'testing'
        self.op = OutputPerceptron(self.inputs, self.neuron_weights, output_key)
        self.assertEqual(self.op.output_key, output_key)