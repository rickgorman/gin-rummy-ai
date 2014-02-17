from gin import *
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


class TestGinHand(unittest.TestCase):

    maxDiff = None

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

    card_data2 = [
        (9, 'h'),
        (9, 'c'),
        (9, 's'),
        (9, 'd'),
        (10, 's'),
        (11, 's'),
        (12, 's'),
        (13, 's'),
        (13, 'c'),
        (13, 'h')
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

    def test_is_in_a_4set(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data2)
        gc_yes = GinCard(Card(9, 'c'))
        gc_no  = GinCard(Card(10, 'c'))

        self.assertEqual(True, g._is_in_a_4set(gc_yes, g.cards))
        self.assertEqual(False, g._is_in_a_4set(gc_no, g.cards))

    def test_enumerate_all_melds_and_sets(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)
        generated_melds = g.enumerate_all_melds_and_sets()
        expected_melds = [[(9, 'c'),  (9, 'h'),  (9, 's')],
                          [(9, 's'),  (10, 's'), (11, 's')],
                          [(10, 's'), (11, 's'), (12, 's')],
                          [(11, 's'), (12, 's'), (13, 's')],
                          [(9, 's'),  (10, 's'), (11, 's'), (12, 's')],
                          [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(9, 's'),  (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(13, 's'), (13, 'c'), (13, 'h')],
        ]

        print "expected melds:  " + ''.join(str(x) for x in expected_melds)
        print "generated melds: " + ''.join(str(x) for x in generated_melds)
        self.assertEqual(generated_melds, expected_melds)


    def testDeadwoodCount(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(5, g.deadwood_count())