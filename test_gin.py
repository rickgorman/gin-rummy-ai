from gin import *
import unittest
import random


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


# noinspection PyProtectedMember
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

    def test_add_card(self):
        g = GinHand()
        self.assertEqual(0, len(g.cards))

        g.add_card(GinCard(5, 'c'))
        self.assertEqual(1, len(g.cards))
        self.assertEqual(5, g.cards[0].rank)
        self.assertEqual('c', g.cards[0].suit)

    def test_discard(self):
        g = GinHand()
        gc = GinCard(5, 'c')
        g.add_card(gc)
        self.assertEqual(1, len(g.cards))
        g.discard(gc)
        self.assertEqual(0, len(g.cards))

    def test_discard_not_holding_said_card(self):
        g = GinHand()
        gc_yes = GinCard(5, 'c')
        gc_no = GinCard(7, 'd')
        g.add_card(gc_yes)
        self.assertEqual(1, len(g.cards))
        g.discard(gc_no)
        self.assertEqual(1, len(g.cards))

    # make sure we handle discarding properly when we have an empty hand
    def test_discard_empty_hand(self):
        g = GinHand()
        gc = GinCard(5, 'c')
        g.discard(gc)
        self.assertEqual(0, len(g.cards))

    def test_sort_hand(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)
        # the add_card function sorts after each add. randomize here to bypass it.
        random.shuffle(g.cards)

        g.sort_hand()
        self.assertEqual(13, g.cards[-1].rank)
        self.assertEqual('s', g.cards[-1].suit)

    def test__melds_using_this_card(self):
        gc = GinCard(5, 'c')
        m = GinHand._melds_using_this_card(gc)

        self.assertEqual(((1, 'c'), (2, 'c'), (3, 'c'), (4, 'c'), (5, 'c')), m[0])
        self.assertEqual(12, len(m))

    def test__is_in_a_meld(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)

        # all cards in card_data1 except for the 5c,9h,9c,Kc,Kh should be marked as being in a meld
        for c in self.card_data1:
            gc = GinCard(c[0], c[1])
            if (c[0] == 5 and c[1] == 'c') or (
                    c[0] == 9  and c[1] == 'c') or (
                    c[0] == 9  and c[1] == 'h') or (
                    c[0] == 13 and c[1] == 'c') or (
                    c[0] == 13 and c[1] == 'h'):
                self.assertEqual(False, g._is_in_a_meld(gc), "Frank: %d, suit: %s" % (gc.rank, gc.suit))
            else:
                self.assertEqual(True, g._is_in_a_meld(gc), "Trank: %d, suit: %s" % (gc.rank, gc.suit))

    def test__is_in_a_3set(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data2)

        self.assertEqual(False, g._is_in_a_3set(GinCard(9, 's')))
        self.assertEqual(False, g._is_in_a_3set(GinCard(10, 's')))
        self.assertEqual(True, g._is_in_a_3set(GinCard(13, 's')))

        # test a card not in the hand
        self.assertEqual(False, g._is_in_a_3set(GinCard(1, 's')))

    def test__is_in_a_4set(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data2)
        gc_yes = GinCard(9, 'c')
        gc_no = GinCard(10, 'c')

        self.assertEqual(True, g._is_in_a_4set(gc_yes))
        self.assertEqual(False, g._is_in_a_4set(gc_no))

        # test a card not in the hand
        self.assertEqual(False, g._is_in_a_4set(GinCard(1, 'c')))

    def test__contains_card(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(True, g._contains_card(5, 'c'))
        self.assertEqual(False, g._contains_card(5, 'd'))

    def test_enumerate_all_melds_and_sets(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)
        generated_melds = g.enumerate_all_melds_and_sets()
        expected_melds = [[(9,  'c'), (9,  'h'), (9,  's')],
                          [(9,  's'), (10, 's'), (11, 's')],
                          [(10, 's'), (11, 's'), (12, 's')],
                          [(11, 's'), (12, 's'), (13, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's')],
                          [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(13, 's'), (13, 'c'), (13, 'h')],
        ]

        self.assertEqual(generated_melds, expected_melds)
        print "expected melds:  " + ''.join(str(x) for x in expected_melds)
        print "generated melds: " + ''.join(str(x) for x in generated_melds)

    def test_enumerate_all_melds_and_sets_quads(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data2)
        generated_melds = g.enumerate_all_melds_and_sets()
        expected_melds = [[(9,  'c'), (9,  'd'), (9,  'h')],
                          [(9,  'c'), (9,  'd'), (9,  's')],
                          [(9,  'c'), (9,  'h'), (9,  's')],
                          [(9,  'd'), (9,  'h'), (9,  's')],
                          [(9,  's'), (10, 's'), (11, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(10, 's'), (11, 's'), (12, 's')],
                          [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(11, 's'), (12, 's'), (13, 's')],
                          [(13, 's'), (13, 'c'), (13, 'h')],
        ]

        self.assertEqual(generated_melds, expected_melds)
        print "expected melds:  " + ''.join(str(x) for x in expected_melds)
        print "generated melds: " + ''.join(str(x) for x in generated_melds)

    def test_deadwood_count(self):
        g = self.helper_generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(5, g.deadwood_count())

    def test__deadwood_count(self):
        pass