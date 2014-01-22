from gin import *
import unittest


class TestGinCard(unittest.TestCase):
    def testNewGinCard(self):
        known_points = [
            (1, Card(1, 'c')),
            (2, Card(2, 'c')),
            (3, Card(3, 'c')),
            (4, Card(4, 'c')),
            (5, Card(5, 'c')),
            (6, Card(6, 'c')),
            (7, Card(7, 'c')),
            (8, Card(8, 'c')),
            (9, Card(9, 'c')),
            (10, Card(10, 'c')),
            (10, Card(11, 'c')),
            (10, Card(12, 'c')),
            (10, Card(13, 'c')),
        ]

        for k in known_points:
            g = GinCard(k[1])
            expected_points = k[0]
            self.assertEqual(expected_points, g.point_value)


class TestGinHand(unittest.TestCase):
    card_data1 = [
        (9, 'h'),
        (9, 'c'),
        (9, 's'),
        (10, 's'),
        (11, 's'),
        (12, 's'),
        (13, 's'),
        (13, 'c'),
        (13, 'h'),
        (5, 'c'),
    ]

    @staticmethod
    def helper_generate_ginhand_from_card_data(cdata):
        g = GinHand()
        for c in cdata:
            g.add_card(Card(c[0], c[1]))
        return g

    def testNewGinHand(self):
        g = GinHand()
        self.assertEqual(0, len(g.cards))

    def test_enumerate_all_melds_and_sets(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(g.enumerate_all_melds_and_sets(),
                         [
                             [(9,  'c'), (9,  'h'), (9,  's')],
                             [(9,  's'), (10, 's'), (11, 's')],
                             [(10, 's'), (11, 's'), (12, 's')],
                             [(11, 's'), (12, 's'), (13, 's')],
                             [(9,  's'), (10, 's'), (11, 's'),  (12, 's')],
                             [(10, 's'), (11, 's'), (12, 's'),  (13, 's')],
                             [(9,  's'), (10, 's'), (11, 's'),  (12, 's'),  (13, 's')],
                             [(13, 's'), (13, 'c'), (13, 'h')],
                         ])


    def testDeadwoodCount(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(5, g.deadwood_count())