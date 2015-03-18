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