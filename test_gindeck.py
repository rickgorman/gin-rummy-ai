# Created by rg on 8/9/14.

from gindeck import *
import unittest


class TestGinCard(unittest.TestCase):
    def testNewGinCard(self):
        known_points = [
            (1, 1, 'c'),
            (2, 2, 'c'),
            (3, 3, 'c'),
            (4, 4, 'c'),
            (5, 5, 'c'),
            (6, 6, 'c'),
            (7, 7, 'c'),
            (8, 8, 'c'),
            (9, 9, 'c'),
            (10, 10, 'c'),
            (10, 11, 'c'),
            (10, 12, 'c'),
            (10, 13, 'c')
        ]

        for k in known_points:
            g = GinCard(k[1], k[2])
            expected_points = k[0]
            self.assertEqual(expected_points, g.point_value)

    def test_to_s(self):
        g = GinCard(9, 'c')
        self.assertEqual('9c', g.to_s())


class TestGinDeck(unittest.TestCase):
    def test_deal_a_card(self):
        gd = GinDeck()

        card = gd.deal_a_card()
        self.assertIsInstance(card, GinCard)