import unittest
from ginstrategy import *


class TestGinStrategy(unittest.TestCase):
    def test__init__(self):
        pass

    def test_best_action(self):
        mgs = MockGinStrategy()

        # ensure mock strategy tells us to discard our first card
        actions = mgs.best_action()
        self.assertEqual(actions, ['DISCARD', 0])

    def test_accept_improper_knock(self):
        self.fail("test not yet written!")
        # note: we need to allow the strategy to decide whether or not to accept an improper knock.
        # - see http://ginrummytournaments.com/pdfs/Rules_2012.pdf Rule #10