import random
from test_helpers import *
from ginhand import *


# noinspection PyProtectedMember
class TestGinCardGroup(Helper):
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
        (1, 'h'),
        (9, 'c'),
        (9, 's'),
        (9, 'd'),
        (10, 's'),
        (11, 's'),
        (12, 's'),
        (5, 's'),
        (5, 'd'),
        (5, 'h')
    ]

    def test___repr__(self):
        card_list = [(1, 'c'), (2, 'd'), (3, 's')]
        gcg = GinCardGroup(card_list)

        self.assertEqual("1c 2d 3s", gcg.__repr__())

    def test___cmp_(self):
        card_group_first  = GinCardGroup([(1, 'c'), (1, 'd'), (1, 'h')])
        card_group_second = GinCardGroup([(1, 'c'), (2, 'c'), (3, 'c')])
        card_group_third  = GinCardGroup([(2, 'c'), (3, 'c'), (4, 'c')])
        card_group_fourth = GinCardGroup([(2, 'c'), (3, 'c'), (4, 'c'), (5, 'c')])

        # test equality
        self.assertEqual(card_group_first.__cmp__(card_group_first), 0)

        # test less than
        self.assertLessEqual(card_group_first.__cmp__(card_group_second), -1)
        self.assertLessEqual(card_group_first.__cmp__(card_group_third), -1)
        self.assertLessEqual(card_group_first.__cmp__(card_group_fourth), -1)
        self.assertLessEqual(card_group_second.__cmp__(card_group_third), -1)
        self.assertLessEqual(card_group_second.__cmp__(card_group_fourth), -1)
        self.assertLessEqual(card_group_third.__cmp__(card_group_fourth), -1)

        # test greater than
        self.assertGreaterEqual(card_group_second.__cmp__(card_group_first), 1)
        self.assertGreaterEqual(card_group_third.__cmp__(card_group_first),  1)
        self.assertGreaterEqual(card_group_third.__cmp__(card_group_second), 1)
        self.assertGreaterEqual(card_group_fourth.__cmp__(card_group_first), 1)
        self.assertGreaterEqual(card_group_fourth.__cmp__(card_group_second), 1)
        self.assertGreaterEqual(card_group_fourth.__cmp__(card_group_third), 1)

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
        expected_melds_data = [[(9,  'c'), (9,  'h'), (9,  's')],
                                [(9,  's'), (10, 's'), (11, 's')],
                                [(9,  's'), (10, 's'), (11, 's'), (12, 's')],
                                [(9,  's'), (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                                [(10, 's'), (11, 's'), (12, 's')],
                                [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                                [(11, 's'), (12, 's'), (13, 's')],
                                [(13, 'c'), (13, 'h'), (13, 's')],
                               ]

        g = self.generate_gincardgroup_from_card_data(self.card_data1)
        generated_melds = g.enumerate_all_melds_and_sets()

        self.compare_arrays_of_cardgroups(expected_melds_data, generated_melds)

    def test_enumerate_all_melds_and_sets_quads(self):
        expected_melds_data = [[(9,  'c'), (9,  'd'), (9,  'h')],
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

        g = self.generate_gincardgroup_from_card_data(self.card_data2)
        generated_melds = g.enumerate_all_melds_and_sets()

        self.compare_arrays_of_cardgroups(expected_melds_data, generated_melds)

    def test_enumerate_all_melds(self):
        expected_melds_data = [[(9,  's'), (10, 's'), (11, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's')],
                          [(9,  's'), (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(10, 's'), (11, 's'), (12, 's')],
                          [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                          [(11, 's'), (12, 's'), (13, 's')],
                          ]

        g = self.generate_gincardgroup_from_card_data(self.card_data2)
        generated_melds = g.enumerate_all_melds()

        self.compare_arrays_of_cardgroups(expected_melds_data, generated_melds)

    def test_enumerate_all_sets(self):
        expected_melds_data = [[(9,  'c'), (9,  'd'), (9,  'h')],
                          [(9,  'c'), (9,  'd'), (9, 'h'), (9, 's')],
                          [(9,  'c'), (9,  'd'), (9,  's')],
                          [(9,  'c'), (9,  'h'), (9,  's')],
                          [(9,  'd'), (9,  'h'), (9,  's')],
                          [(13, 'c'), (13, 'h'), (13, 's')],
                          ]

        g = self.generate_gincardgroup_from_card_data(self.card_data2)
        generated_melds = g.enumerate_all_sets()

        self.compare_arrays_of_cardgroups(expected_melds_data, generated_melds)

    def test__is_in_a_meld(self):
        cgroup = self.generate_gincardgroup_from_card_data(self.card_data1)

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
        g = self.generate_gincardgroup_from_card_data(self.card_data2)

        self.assertEqual(False, g._is_in_a_3set(GinCard(9, 's')))
        self.assertEqual(False, g._is_in_a_3set(GinCard(10, 's')))
        self.assertEqual(True, g._is_in_a_3set(GinCard(13, 's')))

        # test a card not in the hand
        self.assertEqual(False, g._is_in_a_3set(GinCard(1, 's')))

    def test__is_in_a_4set(self):
        g = self.generate_gincardgroup_from_card_data(self.card_data2)
        gc_yes = GinCard(9, 'c')
        gc_no = GinCard(10, 'c')

        self.assertEqual(True, g._is_in_a_4set(gc_yes))
        self.assertEqual(False, g._is_in_a_4set(gc_no))

        # test a card not in the hand
        self.assertEqual(False, g._is_in_a_4set(GinCard(1, 'c')))

    def test_sort_melds__only_melds(self):
        g = self.generate_gincardgroup_from_card_data(self.card_data2)

        expected_melds_data = [[(9,  's'), (10, 's'), (11, 's')],
                                [(9,  's'), (10, 's'), (11, 's'), (12, 's')],
                                [(9,  's'), (10, 's'), (11, 's'), (12, 's'), (13, 's')],
                                [(10, 's'), (11, 's'), (12, 's')],
                                [(10, 's'), (11, 's'), (12, 's'), (13, 's')],
                                [(11, 's'), (12, 's'), (13, 's')],
                               ]

        test_melds = g.enumerate_all_melds()
        shuffle(test_melds)

        sorted_melds = GinCardGroup.sort_melds(test_melds)

        self.compare_arrays_of_cardgroups(expected_melds_data, sorted_melds)

    def test_sort_melds__melds_and_sets(self):
        g = self.generate_gincardgroup_from_card_data(self.card_data2)

        expected_melds_data = [[(9,  'c'), (9,  'd'), (9,  'h')],
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

        test_melds = g.enumerate_all_melds_and_sets()
        shuffle(test_melds)

        sorted_melds = GinCardGroup.sort_melds(test_melds)

        self.compare_arrays_of_cardgroups(expected_melds_data, sorted_melds)

    def test_uniqsort_cardgroups(self):
        # starting with an unsorted aGCG with a duplicate AND a GCG with an out-of-order cards array
        agcg = [GinCardGroup([(1, 'c'), (2, 'c'), (3, 'c')]),
                GinCardGroup([(2, 'd'), (2, 'c'), (2, 'h')]),
                GinCardGroup([(1, 'c'), (2, 'c'), (3, 'c')])]

        cleaned = GinCardGroup.uniqsort_cardgroups(agcg)

        # ensure we dedupe
        self.assertEqual(2, len(cleaned))

        # ensure we sort
        self.assertEqual(cleaned[0].__repr__(), "1c 2c 3c")
        self.assertEqual(cleaned[1].__repr__(), "2c 2d 2h")


# noinspection PyProtectedMember
class TestGinHand(Helper):
    maxDiff = None

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

    def test_size(self):
        g = GinHand()
        self.assertEqual(0, g.size())
        g.add(9, 'c')
        self.assertEqual(1, g.size())
        g.discard(g.cg.cards.pop())
        self.assertEqual(0, g.size())

    def test_get_card_at_index(self):
        g = self.generate_ginhand_from_card_data(self.card_data1)

        target = g.get_card_at_index(0)
        self.assertEqual(target, g.cg.cards[0])

    def test__sort_hand(self):
        g = self.generate_ginhand_from_card_data(self.card_data1)
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
        g = self.generate_ginhand_from_card_data(self.card_data1)
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
        g = self.generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(True, g._contains_card(5, 'c'))
        self.assertEqual(False, g._contains_card(5, 'd'))

    def test__clean_meld_group(self):
        pruner_meld = GinCardGroup([(9, 'c'), (10, 'c'), (11, 'c')])

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

        cleaned = GinHand._prune_meld_group(melds, pruner_meld)

        self.assertEqual(8, len(cleaned))

    def test__prune_meld_group(self):
        a = GinCardGroup([(9, 'c'), (10, 'c'), (11, 'c')])
        b = GinCardGroup([(9, 'c'), (9,  'h'), (9,  's')])
        c = GinCardGroup([(1, 'c'), (2,  'c'), (3,  'c')])
        p = GinCardGroup([(9, 'c')])
        melds = [a, b, c]

        pruned = GinHand._prune_meld_group(melds, p)
        self.assertEqual(1, len(pruned))

    def test__prune_meld_group_empty_pruner(self):
        a = GinCardGroup([(9, 'c'), (10, 'c'), (11, 'c')])
        b = GinCardGroup([(9, 'c'), (9,  'h'), (9,  's')])
        c = GinCardGroup([(1, 'c'), (2,  'c'), (3,  'c')])
        p = GinCardGroup()
        melds = [a, b, c]

        pruned = GinHand._prune_meld_group(melds, p)
        self.assertEqual(3, len(pruned))

    def test_deadwood_count(self):
        g1 = self.generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(5, g1.deadwood_count())

        g2 = self.generate_ginhand_from_card_data(self.card_data2)
        self.assertEqual(0, g2.deadwood_count())

        g3 = self.generate_ginhand_from_card_data(self.card_data3)
        self.assertEqual(26, g3.deadwood_count())

    def test__examine_melds(self):
        # empty hand = 0 deadwood
        empty_hand = GinHand()
        self.assertEqual(0, empty_hand._examine_melds(empty_hand.cg))

        # 1c,2d hand = 3 deadwood
        two_card_hand = GinHand()
        two_card_hand.add_card(GinCard(1, 'c'))
        two_card_hand.add_card(GinCard(2, 'd'))
        self.assertEqual(3, two_card_hand._examine_melds(two_card_hand.cg))

        # 1c,2d,3h hand = 6 deadwood
        three_card_hand = GinHand()
        three_card_hand.add_card(GinCard(1, 'c'))
        three_card_hand.add_card(GinCard(2, 'd'))
        three_card_hand.add_card(GinCard(3, 'h'))
        self.assertEqual(6, three_card_hand._examine_melds(three_card_hand.cg))

        # 1c,2d,3h,4h,5h hand = 3 deadwood
        five_card_hand = GinHand()
        five_card_hand.add_card(GinCard(1, 'c'))
        five_card_hand.add_card(GinCard(2, 'd'))
        five_card_hand.add_card(GinCard(3, 'h'))
        five_card_hand.add_card(GinCard(4, 'h'))
        five_card_hand.add_card(GinCard(5, 'h'))
        self.assertEqual(3, five_card_hand._examine_melds(five_card_hand.cg))

        g = self.generate_ginhand_from_card_data(self.card_data1)
        self.assertEqual(5, g._examine_melds(g.cg))

    def test_deadwood_cards(self):
        gh = self.generate_ginhand_from_card_data(self.card_data1)

        self.assertIsInstance(gh.deadwood_cards(), GinCardGroup)
        self.assertEqual(gh.deadwood_cards().contains(5, 'c'))

    def test_process_layoff(self):
        gh_layer = self.generate_ginhand_from_card_data(self.card_data1)
        gh_winner = self.generate_ginhand_from_card_data(self.card_data3)

        # we lay off our single unmatched 5 against a set of 5's and expect a new deadwood count of 0
        self.assertIsInstance(gh_layer.process_layoff(gh_winner), GinHand)
        self.assertEqual(gh_layer.process_layoff(gh_winner).deadwood_count(), 0)