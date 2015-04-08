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

    def best_action(self):
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

    def test_best_action(self):
        strat = MockGinStrategy(['DISCARD', 0])

        # ensure mock strategy tells us to discard our first card
        self.assertEqual(strat.best_action(), ['DISCARD', 0])

    def test_decode_signal(self):
        # ensure we are returning the proper signal for a given neural network's output.
        # silly smell: this code duplicates the implementation code
        signal_range = [x * 0.05 for x in range(0, 20)]
        bucket_range = range(2, 10)
        for signal in signal_range:
            for bucket in bucket_range:
                decoded = GinStrategy.decode_signal(signal, buckets=bucket)
                self.assertEqual(decoded, signal * float(bucket) - 1)


class TestNeuralGinStrategy(Helper):
    def setUp(self):
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()
        self.gm = GinMatch(self.p1, self.p2)

        self.nn = MockNeuralNetwork(None, None, accept_improper_knock=True)
        self.strat = NeuralGinStrategy(self.p1, self.p2, self.gm, self.nn)

    def test_consider_accepting_improper_knock(self):
        # verify that we return the mock's output
        self.assertTrue(self.strat.consider_accepting_improper_knock())
