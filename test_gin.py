from gin import *
import unittest
import random


class Helper():
    @staticmethod
    def helper_generate_ginhand_from_card_data(cdata):
        g = GinHand()
        for c in cdata:
            g.add_card(GinCard(c[0], c[1]))
        return g

    @staticmethod
    def helper_generate_gincardgroup_from_card_data(cdata):
        cg = GinCardGroup()
        for c in cdata:
            cg.add(c[0], c[1])
        return cg


# noinspection PyProtectedMember
class TestGinCardGroup(unittest.TestCase):
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


    def test_new_gincardgroup(self):
        cg = GinCardGroup(self.card_data1)

        self.assertEqual(10, len(cg.cards))

    def test_new_gincardgroup_empty(self):
        cg = GinCardGroup()
        self.assertEqual(0, len(cg.cards))

    def test_add(self):
        cg = GinCardGroup()
        cg.add(9, 'c')
        self.assertEqual(1, len(cg.cards))
        self.assertEqual(9, cg.cards[0].rank)
        self.assertEqual('c', cg.cards[0].suit)

    def test_add_card(self):
        cg = GinCardGroup()
        c = GinCard(7, 'h')
        cg.add_card(c)
        self.assertEqual(1, len(cg.cards))
        self.assertEqual(7, cg.cards[0].rank)
        self.assertEqual('h', cg.cards[0].suit)

    def test_remove(self):
        cg = GinCardGroup(self.card_data1)
        cg.remove(GinCard(9, 'c'))
        self.assertEqual(9, len(cg.cards))

    def test_remove_non_card(self):
        cg = GinCardGroup(self.card_data1)
        cg.remove(GinCard(2, 'c'))
        self.assertEqual(10, len(cg.cards))

    def test_size(self):
        cg = GinCardGroup()
        self.assertEqual(0, cg.size())
        cg.add(2, 'd')
        self.assertEqual(1, cg.size())

    def test_contains(self):
        cg = GinCardGroup(self.card_data1)
        self.assertEqual(True, cg.contains(5, 'c'))
        self.assertEqual(False, cg.contains(5, 'd'))

    def test_contains_card(self):
        cg = GinCardGroup(self.card_data1)
        card_yes = GinCard(5, 'c')
        card_no  = GinCard(5, 'd')

        self.assertEqual(True, cg.contains_card(card_yes))
        self.assertEqual(False, cg.contains_card(card_no))

    def test_sum_points(self):
        cg = GinCardGroup(self.card_data1)
        self.assertEqual(92, cg.sum_points())

    def test_sum_points_zero(self):
        cg = GinCardGroup()
        self.assertEqual(0, cg.sum_points())

    def test_enumerate_all_melds_and_sets(self):
        g = Helper.helper_generate_ginhand_from_card_data(self.card_data1)
        generated_melds = g.cg.enumerate_all_melds_and_sets()
        expected_melds_data = [[(9,  'c'), (9,  'h'), (9,  's')],
                                [(9,  's'), (10, 's'), (11, 's')],
                                [(9,  's'), (10, 's'), (11, 's'), (12, 's')],
                                [(9,  's'), (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                                [(10, 's'), (11, 's'), (12, 's')],
                                [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                                [(11, 's'), (12, 's'), (13, 's')],
                                [(13, 'c'), (13, 'h'), (13, 's')],
                               ]

        expected_melds = []
        for meld in expected_melds_data:
            expected_melds.append(GinCardGroup(meld))
#        print "expected melds:  " + ''.join(str(x) for x in expected_melds)
#        print "generated melds: " + ''.join(str(x) for x in generated_melds)
        self.assertEqual(generated_melds, expected_melds)

    def test_enumerate_all_melds_and_sets_quads(self):
        g = Helper.helper_generate_ginhand_from_card_data(self.card_data2)
        generated_melds = g.enumerate_all_melds_and_sets()
        expected_melds = [[(9,  'c'), (9,  'd'), (9,  'h')],
                          [(9,  'c'), (9,  'd'), (9,  'h'), (9, 's')],
                          [(9,  'c'), (9,  'd'), (9,  's')],
                          [(9,  'c'), (9,  'h'), (9,  's')],
                          [(9,  'd'), (9,  'h'), (9,  's')],
                          [(9,  's'), (10, 's'), (11, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(10, 's'), (11, 's'), (12, 's')],
                          [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(11, 's'), (12, 's'), (13, 's')],
                          [(13, 'c'), (13, 'h'), (13, 's')],
                          ]

#        print "expected melds:  " + ''.join(str(x) + ",\n" for x in expected_melds)
#        print "generated melds: " + ''.join(str(x) + ",\n" for x in generated_melds)
        self.assertEqual(generated_melds, expected_melds)

    def test__is_in_a_meld(self):
        cgroup = Helper.helper_generate_gincardgroup_from_card_data(self.card_data1)

        # all cards in card_data1 except for the 5c,9h,9c,Kc,Kh should be marked as being in a meld
        for c in self.card_data1:
            gc = GinCard(c[0], c[1])
            if (c[0] == 5 and c[1] == 'c') or (
                    c[0] == 9  and c[1] == 'c') or (
                    c[0] == 9  and c[1] == 'h') or (
                    c[0] == 13 and c[1] == 'c') or (
                    c[0] == 13 and c[1] == 'h'):
                self.assertEqual(False, cgroup._is_in_a_meld(gc), "F-rank: %d, suit: %s" % (gc.rank, gc.suit))
            else:
                self.assertEqual(True, cgroup._is_in_a_meld(gc), "T-rank: %d, suit: %s" % (gc.rank, gc.suit))

    def test__is_in_a_3set(self):
        g = Helper.helper_generate_gincardgroup_from_card_data(self.card_data2)

        self.assertEqual(False, g._is_in_a_3set(GinCard(9, 's')))
        self.assertEqual(False, g._is_in_a_3set(GinCard(10, 's')))
        self.assertEqual(True, g._is_in_a_3set(GinCard(13, 's')))

        # test a card not in the hand
        self.assertEqual(False, g._is_in_a_3set(GinCard(1, 's')))

    def test__is_in_a_4set(self):
        g = Helper.helper_generate_gincardgroup_from_card_data(self.card_data2)
        gc_yes = GinCard(9, 'c')
        gc_no = GinCard(10, 'c')

        self.assertEqual(True, g._is_in_a_4set(gc_yes))
        self.assertEqual(False, g._is_in_a_4set(gc_no))

        # test a card not in the hand
        self.assertEqual(False, g._is_in_a_4set(GinCard(1, 'c')))

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

    card_data3 = [
        (2, 'h'),
        (2, 'c'),
        (2, 'd'),
        (3, 'h'),
        (3, 'c'),
        (3, 's'),
        (4, 'c'),
        (5, 'c'),
        (11, 's'),
        (13, 'h')
    ]

    def testNewGinHand(self):
        g = GinHand()
        self.assertEqual(0, g.cg.size())

    def test_add(self):
        g = GinHand()
        g.add(9, 'c')
        self.assertEqual(9, g.cg.cards[0].rank)
        self.assertEqual('c', g.cg.cards[0].suit)

    def test_add_card(self):
        g = GinHand()
        self.assertEqual(0,g.cg.size())

        g.add_card(GinCard(5, 'c'))
        self.assertEqual(1,g.cg.size())
        self.assertEqual(5, g.cg.cards[0].rank)
        self.assertEqual('c', g.cg.cards[0].suit)

    def test_discard(self):
        g = GinHand()
        gc = GinCard(5, 'c')
        g.add_card(gc)
        self.assertEqual(1, g.cg.size())
        g.discard(gc)
        self.assertEqual(0, g.cg.size())

    def test_discard_not_holding_said_card(self):
        g = GinHand()
        gc_yes = GinCard(5, 'c')
        gc_no = GinCard(7, 'd')
        g.add_card(gc_yes)
        self.assertEqual(1, g.cg.size())
        g.discard(gc_no)
        self.assertEqual(1, g.cg.size())

    # make sure we handle discarding properly when we have an empty hand
    def test_discard_empty_hand(self):
        g = GinHand()
        gc = GinCard(5, 'c')
        g.discard(gc)
        self.assertEqual(0, g.cg.size())

    def test__sort_hand(self):
        g = Helper.helper_generate_ginhand_from_card_data(self.card_data1)
        # the add_card function sorts after each add. randomize here to bypass it.
        random.shuffle(g.cg.cards)

        g._sort_hand()
        # 5c should be first
        self.assertEqual(5, g.cg.cards[0].rank)
        self.assertEqual('c', g.cg.cards[0].suit)
        # 9c should be second
        self.assertEqual(9, g.cg.cards[1].rank)
        self.assertEqual('c', g.cg.cards[1].suit)
        # Kc should be third
        self.assertEqual(9, g.cg.cards[2].rank)
        self.assertEqual('h', g.cg.cards[2].suit)
        # Ks should be fourth
        self.assertEqual(9, g.cg.cards[3].rank)
        self.assertEqual('s', g.cg.cards[3].suit)
        # 5c should be fifth
        self.assertEqual(10, g.cg.cards[4].rank)
        self.assertEqual('s', g.cg.cards[4].suit)
        # 9c should be sixth
        self.assertEqual(11, g.cg.cards[5].rank)
        self.assertEqual('s', g.cg.cards[5].suit)
        # Kc should be seventh
        self.assertEqual(12, g.cg.cards[6].rank)
        self.assertEqual('s', g.cg.cards[6].suit)
        # Ks should be eighth
        self.assertEqual(13, g.cg.cards[7].rank)
        self.assertEqual('c', g.cg.cards[7].suit)
        # Kc should be ninth
        self.assertEqual(13, g.cg.cards[8].rank)
        self.assertEqual('h', g.cg.cards[8].suit)
        # Ks should be tenth
        self.assertEqual(13, g.cg.cards[-1].rank)
        self.assertEqual('s', g.cg.cards[-1].suit)

    def test__sort_hand_by_suit(self):
        g = Helper.helper_generate_ginhand_from_card_data(self.card_data1)
        random.shuffle(g.cg.cards)

        g._sort_hand(by_suit=True)
        # 5c should be first
        self.assertEqual(5, g.cg.cards[0].rank)
        self.assertEqual('c', g.cg.cards[0].suit)
        # 9c should be second
        self.assertEqual(9, g.cg.cards[1].rank)
        self.assertEqual('c', g.cg.cards[1].suit)
        # Kc should be third
        self.assertEqual(13, g.cg.cards[2].rank)
        self.assertEqual('c', g.cg.cards[2].suit)
        # Ks should be fourth
        self.assertEqual(9, g.cg.cards[3].rank)
        self.assertEqual('h', g.cg.cards[3].suit)
        # 5c should be fifth
        self.assertEqual(13, g.cg.cards[4].rank)
        self.assertEqual('h', g.cg.cards[4].suit)
        # 9c should be sixth
        self.assertEqual(9, g.cg.cards[5].rank)
        self.assertEqual('s', g.cg.cards[5].suit)
        # Kc should be seventh
        self.assertEqual(10, g.cg.cards[6].rank)
        self.assertEqual('s', g.cg.cards[6].suit)
        # Ks should be eighth
        self.assertEqual(11, g.cg.cards[7].rank)
        self.assertEqual('s', g.cg.cards[7].suit)
        # Kc should be ninth
        self.assertEqual(12, g.cg.cards[8].rank)
        self.assertEqual('s', g.cg.cards[8].suit)
        # Ks should be tenth
        self.assertEqual(13, g.cg.cards[-1].rank)
        self.assertEqual('s', g.cg.cards[-1].suit)

    def test_sum_points(self):
        g = GinHand()
        self.assertEqual(0, g.points())

        g.add(9, 'c')
        self.assertEqual(9, g.points())

        g.add(11, 'c')
        self.assertEqual(19, g.points())

    def test__melds_using_this_card(self):
        gc = GinCard(5, 'c')
        m = GinHand._melds_using_this_card(gc)

        self.assertEqual(((1, 'c'), (2, 'c'), (3, 'c'), (4, 'c'), (5, 'c')), m[0])
        self.assertEqual(12, len(m))

    def test__contains_card(self):
        g = Helper.helper_generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(True, g._contains_card(5, 'c'))
        self.assertEqual(False, g._contains_card(5, 'd'))

    def test__clean_meld_group(self):
        base_meld = GinCardGroup([(9, 'c'), (10, 'c'), (11, 'c')])

        meld_data = [[(9,  'c'), (9,  'd'), (9,  'h')],
                          [(9,  'c'), (9,  'd'), (9,  'h'), (9, 's')],
                          [(9,  'c'), (9,  'd'), (9,  's')],
                          [(9,  'c'), (9,  'h'), (9,  's')],
                          [(9,  'd'), (9,  'h'), (9,  's')],
                          [(9,  's'), (10, 's'), (11, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(10, 's'), (11, 's'), (12, 's')],
                          [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(11, 's'), (12, 's'), (13, 's')],
                          [(13, 'c'), (13, 'h'), (13, 's')]
                         ]

        melds = []
        for data in meld_data:
            melds.append(GinCardGroup(data))

        cleaned = GinHand._clean_meld_group(base_meld, melds)

        self.assertEqual(8, len(cleaned))

    def test_deadwood_count(self):
        g3 = Helper.helper_generate_ginhand_from_card_data(self.card_data3)
        self.assertEqual(26, g3.deadwood_count())

        g1 = Helper.helper_generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(5, g1.deadwood_count())

        g2 = Helper.helper_generate_ginhand_from_card_data(self.card_data2)
        self.assertEqual(0, g2.deadwood_count())


    def test__examine_melds(self):
        pass
