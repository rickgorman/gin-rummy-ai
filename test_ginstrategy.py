import unittest
from ginstrategy import *
from test_helpers import *
from ginplayer import *
from ginmatch import *
from test_neuralnet import MockNeuralNetwork


# noinspection PyMethodMayBeStatic,PyMissingConstructor
class MockGinStrategy(GinStrategy):
    def __init__(self, mockaction=None):
        if mockaction is None:
            self.action = ['DISCARD', 0]
        else:
            self.action = mockaction

    def determine_best_action(self, phase):
        # by default, we discard the first card
        return self.action

    def consider_accepting_improper_knock(self):
        return True


# noinspection PyAttributeOutsideInit,PyProtectedMember
class TestGinStrategy(Helper):
    def setUp(self):
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()
        self.gm = GinMatch(self.p1, self.p2)

        self.p1_strat = GinStrategy(self.p1, self.p2, self.gm)
        self.p2_strat = GinStrategy(self.p2, self.p1, self.gm)

    def test__init__(self):
        with self.assertRaises(AssertionError):
            GinStrategy(self.p1, self.p1, self.gm)

    def test_determine_best_action(self):
        strat = MockGinStrategy(['DISCARD', 0])

        # ensure mock strategy tells us to discard our first card
        self.assertEqual(strat.determine_best_action(phase='end'), ['DISCARD', 0])


class TestNeuralGinStrategy(Helper):
    def setUp(self):
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()
        self.gm = GinMatch(self.p1, self.p2)

        self.nn = MockNeuralNetwork(None, None, accept_improper_knock=0.9)
        self.strat = NeuralGinStrategy(self.p1, self.p2, self.gm, self.nn)

    def test_consider_accepting_improper_knock(self):
        # verify that we return the mock's output
        self.assertTrue(True is self.strat.consider_accepting_improper_knock())

    def test_decode_signal(self):
        # ensure we are returning the proper signal for a given neural network's output.
        # signals[n] = [input, #buckets, expected output]
        signals = [[0.0, 3, 0],
                   [0.1, 3, 0],
                   [0.2, 3, 0],
                   [0.4, 3, 1],
                   [0.6, 3, 1],
                   [0.7, 3, 2],
                   [1.0, 3, 2],
                   [0.0, 4, 0],
                   [0.10, 4, 0],
                   [0.24, 4, 0],
                   [0.26, 4, 1],
                   [0.51, 4, 2],
                   [0.76, 4, 3],
                   [1.00, 4, 3],
                   [0.00, 10, 0],
                   [0.11, 10, 1],
                   [0.21, 10, 2],
                   [0.41, 10, 4],
                   [0.61, 10, 6],
                   [0.71, 10, 7],
                   [1.00, 10, 9]]

        for signal in signals:
            invalue = signal[0]
            num_buckets = signal[1]
            expected = signal[2]
            decoded = NeuralGinStrategy.decode_signal(invalue, buckets=num_buckets)
            self.assertEqual(expected, decoded)

    def test_decode_best_action_phase_start(self):
        signals = {'PICKUP-FROM-DISCARD': 0.3, 'DRAW': 0.9}

        for action, signal_strength in signals.items():
            self.strat.nn.outputs['action'] = signal_strength
            self.assertEqual(action, self.strat.decode_best_action(phase='start'))

    def test_decode_best_action_phase_end(self):
        signals = {'KNOCK': 0.1, 'DISCARD': 0.5, 'KNOCK-GIN': 0.7}

        for action, signal_strength in signals.items():
            self.strat.nn.outputs['action'] = signal_strength
            self.assertEqual(action, self.strat.decode_best_action(phase='end'))

    # return the index of the card we wish to toss
    def test_decode_index(self):
        signals = {0: 0.08, 1: 0.18, 2: 0.25, 3: 0.34, 4: 0.43, 9: 0.88, 10: 0.97}  # card_index:signal

        for card_index, signal in signals.items():
            self.nn.outputs['index'] = signal
            self.assertEqual(card_index, self.strat.decode_index())

    def test_determine_best_action(self):
        # we test most of this in the above two tests
        pass