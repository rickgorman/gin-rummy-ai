#!/usr/bin/python
#
# ginhand.py
#
# 2014/01/18
# rg
#
# base classes for gin rummy

from deck import *
from operator import attrgetter, itemgetter
from gindeck import *
from utility import *


# card organization and management. takes as input an array of card tuples. maintains objects internally as GinCards
# noinspection PyUnusedLocal
class GinCardGroup:
    def __init__(self, card_list=None):
        self.cards = []
        if card_list is not None:
            for card in card_list:
                self.add_card(card)

    # display contents while debugging
    def __repr__(self):
        description = ""
        for c in self.cards:
            description += str(c.rank)
            description += c.suit
            description += " "

        return description.strip()

    def __cmp__(self, other):
        return cmp(self.cards, other.cards)

    # required for iteration
    def __getitem__(self, index):
        return self.cards[index]

    # required for iteration
    def __len__(self):
        return len(self.cards)

    def __hash__(self):
        return hash(self.cards.__repr__())

    # add a card. guarantee sort.
    def add_card(self, card):
        assert isinstance(card, Card), "trying to add something that isn't a card"
        self.cards.append(card)
        self.sort()

    # discard a Card
    def discard(self, requested):
        for c in self.cards:
            if c.rank == requested.rank and c.suit == requested.suit:
                self.cards.remove(c)

    # sort by rank, suit.  option to reverse sort order.
    def sort(self, by_suit=False):
        if by_suit:
            self.cards.sort(key=attrgetter('suit', 'rank'))
        else:
            self.cards.sort(key=attrgetter('rank', 'suit'))

    # test presence of a card tuple
    def contains(self, rank, suit):
        if any(c.rank == rank and c.suit == suit for c in self.cards):
            return True
        else:
            return False

    # return card at specific index (0-10)
    def get_card_at_index(self, index):
        if index > 10 or index < 0:
            raise Exception
        else:
            return self.cards[index]

    # Card-wrapper for contains()
    def contains_card(self, card):
        return self.contains(card.rank, card.suit)

    def size(self):
        count = 0
        for _ in self.cards:
            count += 1
        return count

    def points(self):
        total = 0
        for card in self.cards:
            total += card.point_value
        return total

    # check to see if a given card is in a meld that exists in this GinCardGroup. Note that this handles 3, 4 and
    # 5-melds as the latter varieties require the existence of the former in order to exist. We must have a 3-meld
    # containing a 456 in order to have a 4-meld containing a 4567.
    def _is_in_a_meld(self, card):
        # must have at least 3 cards to have a set
        if len(self.cards) < 3:
            return False

        answer = False

        # for aces we must have A23
        if card.rank == 1:    # Ace
            if self.contains(2, card.suit) and self.contains(3, card.suit):
                answer = True
            else:
                answer = False

        # for deuces we can have A23 or 234
        elif card.rank == 2:  # 2
            if self.contains(1, card.suit) and self.contains(3, card.suit):
                answer = True
            elif self.contains(3, card.suit) and self.contains(4, card.suit):
                answer = True
            else:
                answer = False

        # for kings we must have exactly JQK
        elif card.rank == 13:  # King
            if self.contains(11, card.suit) and self.contains(12, card.suit):
                answer = True
            else:
                answer = False

        # for queens we can have JQK or TJQ
        elif card.rank == 12:  # Queen
            if self.contains(11, card.suit) and self.contains(13, card.suit):
                answer = True
            elif self.contains(10, card.suit) and self.contains(11, card.suit):
                answer = True
            else:
                answer = False

        # for all other cards, we can have [card-2,card-1,card], [card-1,card,card+1] or [card,card+1,card+2]
        else:
            if self.contains(card.rank - 2, card.suit) and self.contains(card.rank - 1, card.suit):
                answer = True
            elif self.contains(card.rank - 1, card.suit) and self.contains(card.rank + 1, card.suit):
                answer = True
            elif self.contains(card.rank + 1, card.suit) and self.contains(card.rank + 2, card.suit):
                answer = True
            else:
                answer = False

        return answer

    # determine if a card is part of a three-of-a-kind (but not a 4-set)
    def _is_in_a_3set(self, gincard):
        # we need to find exactly two other cards of the same rank
        matches = [x for x in self.cards if x.rank == gincard.rank and x.suit != gincard.suit]
        if len(matches) == 2:
            return True
        else:
            return False

    # determine if a card is part of a four-of-a-kind
    def _is_in_a_4set(self, gincard):
        # we need to find exactly three other cards of the same rank
        matches = [x for x in self.cards if x.rank == gincard.rank and x.suit != gincard.suit]
        if len(matches) == 3:
            return True
        else:
            return False

    # return an array of GinCardGroups of all melds and sets that can be built with the cards in this hand
    def enumerate_all_melds_and_sets(self):

        all_melds = self.enumerate_all_melds()
        all_sets = self.enumerate_all_sets()

        everything = all_melds + all_sets
        GinCardGroup.sort_melds(everything)

        return everything

    @staticmethod
    @memoized
    def _memoized_enumerate_all_melds(hand):
        agcg_all_melds = list()

        # First, check for exact 3-melds
        if hand.size() >= 3:
            hand.sort(by_suit=True)
            for i in range(0, len(hand.cards) - 3 + 1):
                first_card = hand.cards[i]
                second_card = hand.cards[i + 1]
                third_card = hand.cards[i + 2]
                if first_card.suit == second_card.suit == third_card.suit:
                    if first_card.rank + 1 == second_card.rank and second_card.rank + 1 == third_card.rank:
                        agcg_all_melds.append(GinCardGroup([first_card, second_card, third_card]))

        # Next, check for exact 4-melds
        if hand.size() >= 4:
            for i in range(0, len(hand.cards) - 4 + 1):
                first_card = hand.cards[i]
                second_card = hand.cards[i + 1]
                third_card = hand.cards[i + 2]
                fourth_card = hand.cards[i + 3]
                if first_card.suit == second_card.suit == third_card.suit == fourth_card.suit:
                    if (first_card.rank + 1 == second_card.rank and
                                    second_card.rank + 1 == third_card.rank and
                                    third_card.rank + 1 == fourth_card.rank):
                        agcg_all_melds.append(GinCardGroup([first_card, second_card, third_card, fourth_card]))

        # Finally, check for exact 5-melds
        if hand.size() >= 5:
            for i in range(0, len(hand.cards) - 5 + 1):
                first_card = hand.cards[i]
                second_card = hand.cards[i + 1]
                third_card = hand.cards[i + 2]
                fourth_card = hand.cards[i + 3]
                fifth_card = hand.cards[i + 4]
                if first_card.suit == second_card.suit == third_card.suit == fourth_card.suit == fifth_card.suit:
                    if (first_card.rank + 1 == second_card.rank and
                                    second_card.rank + 1 == third_card.rank and
                                    third_card.rank + 1 == fourth_card.rank and
                                    fourth_card.rank + 1 == fifth_card.rank):
                        agcg_all_melds.append(
                            GinCardGroup([first_card, second_card, third_card, fourth_card, fifth_card]))

        agcg_all_melds_deduped = GinCardGroup.uniqsort_cardgroups(agcg_all_melds)

        return agcg_all_melds_deduped

    # return an array of GinCardGroups of all melds that can be built with the cards in this hand
    def enumerate_all_melds(self):
        # easy out. we must have at least 3 cards to have a meld.
        if self.size() < 3:
            return GinCardGroup()
        else:
            return GinHand._memoized_enumerate_all_melds(self)

    @staticmethod
    @memoized
    def _memoized_enumerate_all_sets(hand):
        agcg_all_sets = list()

        # we need at least 3 cards to make a set
        if hand.size() >= 3:
            for c in hand.cards:
                # First, check for 4-sets
                if hand._is_in_a_4set(c):
                    quad_cards = []
                    # enumerate all cards in the 4-set for ease of use
                    for s in c.all_suits():
                        quad_cards.append(GinCard(c.rank, s))

                    # store the 4-set
                    agcg_all_sets.append(GinCardGroup([quad_cards[0], quad_cards[1], quad_cards[2], quad_cards[3]]))

                    # When a 4-card set is found, also store all 4 of the possible 3-card melds
                    agcg_all_sets.append(GinCardGroup([quad_cards[0], quad_cards[1], quad_cards[2]]))
                    agcg_all_sets.append(GinCardGroup([quad_cards[1], quad_cards[2], quad_cards[3]]))
                    agcg_all_sets.append(GinCardGroup([quad_cards[2], quad_cards[3], quad_cards[0]]))
                    agcg_all_sets.append(GinCardGroup([quad_cards[3], quad_cards[0], quad_cards[1]]))
                # Next, check for 3-sets (reminder: here we check for 3sets exclusive of 4sets)
                elif hand._is_in_a_3set(c):
                    set_cards = [x for x in hand.cards if x.rank == c.rank]
                    agcg_all_sets.append(GinCardGroup(set_cards))

        agcg_all_sets_deduped = GinCardGroup.uniqsort_cardgroups(agcg_all_sets)

        return agcg_all_sets_deduped

    # return a sorted array of GinCardGroups, one containing each set
    def enumerate_all_sets(self):
        return GinHand._memoized_enumerate_all_sets(self)

    # return a GCG containing our deadwood cards
    def deadwood_cards(self):

        deadwood = GinCardGroup()
        for c in self.cards:
            if not self._is_in_a_3set(c) and not self._is_in_a_4set(c) and not self._is_in_a_meld(c):
                deadwood.add_card(c)

        return deadwood

    @staticmethod
    @memoized
    def _memoized_deadwood_count(hand):
        debug_func = False
        # begin with worst case: entire hand is deadwood.
        worst_case = hand.points()

        # optimization step: we remove all cards not part of a set or a meld
        specimen = GinCardGroup()
        early_deadwood = GinCardGroup()
        for card in hand.cards:
            if hand._is_in_a_meld(card) or hand._is_in_a_3set(card) or hand._is_in_a_4set(card):
                specimen.add_card(card)
            else:
                early_deadwood.add_card(card)

        if debug_func:
            print "early_deadwood: " + str(early_deadwood.points())
            all_melds = specimen.enumerate_all_melds_and_sets()
            print "all_melds:"
            for meld in all_melds:
                print '\t' + ''.join((x.to_s() + '\t') for x in meld.cards)

        # recursion. add smallest discovered deadwood count to early_deadwood count
        explored_case = hand._examine_melds(specimen) + early_deadwood.points()

        lowest_deadwood = min(worst_case, explored_case)

        if debug_func:
            print "lowest_deadwood: " + str(lowest_deadwood)

        return lowest_deadwood

    def deadwood_count(self):
        return GinHand._memoized_deadwood_count(self)

    # our recursive call for deadwood_count
    # parameters:
    #   cg          a GinCardGroup, representing cards to examine
    @staticmethod
    def _examine_melds(cg, indent_level=0):
        debug_func = False
        if debug_func:
            indent_print(indent_level, "examine_melds[d=" + str(indent_level) + "]: " + \
                                       ''.join((str(x.to_s()) + '\t') for x in cg.cards))

        # no cards means we're holding zero deadwood.
        if cg.size() == 0:
            return 0

        # holding 1 or 2 cards means we're holding pure deadwood. return the sum.
        if cg.size() < 3:
            return sum(card.rank for card in cg.cards)

        # enumeration step: generate all melds possible from our specimen
        all_melds = cg.enumerate_all_melds_and_sets()

        # ceiling is case where entire hand is deadwood (note that this is only for the subset cg, not a 10 card hand)
        minimum_deadwood = cg.points()

        # The recursion. One by one, we enumerate through all possible meld combinations we can make using this subset
        #  of cards, tracking the lowest deadwood value.
        for excluded_meld in all_melds:
            if debug_func:
                indent_print(indent_level, "excluded meld: ".join((str(x.to_s()) + '\t') for x in excluded_meld.cards))

            # create a list of cards to examine, excluding cards in the excluded_meld
            cards_to_examine = GinCardGroup()
            for card in cg.cards:
                for excluded_card in excluded_meld.cards:
                    if card.rank != excluded_card.rank and card.suit != excluded_card.suit:
                        cards_to_examine.add_card(card)
                        break

            # recursive call
            result = GinCardGroup._examine_melds(cards_to_examine, indent_level + 1)

            if debug_func:
                indent_print(indent_level, "deadwood: " + str(result) + "\n")

            # track lowest deadwood
            minimum_deadwood = min(minimum_deadwood, result)

        return minimum_deadwood

    # Given an array of GinCardGroups as melds, we return all melds not containing cards in a given pruner GinCardGroup.
    # This allows us to reduce the list of melds we are interested in exploring.
    @staticmethod
    def _prune_meld_group(agcg_melds, pruner_meld):

        # if we're given an empty base_meld to prune with, don't do any pruning
        if len(pruner_meld.cards) == 0:
            return agcg_melds

        pruned = []
        for meld in agcg_melds:
            for card in pruner_meld.cards:
                # test for the presence of card in meld
                if meld.contains_card(card):
                    break

                # record meld, preventing duplicates
                if meld not in pruned:
                    pruned.append(meld)

        return pruned

    # takes in an array of GCG's and returns them in sorted fashion
    @staticmethod
    def sort_melds(agcg_to_sort):
        # sort the contents of each meld. f3 from http://www.peterbe.com/plog/uniqifiers-benchmark
        for m in agcg_to_sort:
            m.sort()

        agcg_to_sort.sort()

        return agcg_to_sort

    @staticmethod
    def uniqsort_cardgroups(agcg_to_clean):
        # deduplicate using the __repr__() of each GCG as its unique representation
        keys = {}
        for gcg in agcg_to_clean:
            keys[gcg.__repr__()] = gcg
        agcg_cleaned = keys.values()

        # sort
        GinCardGroup.sort_melds(agcg_cleaned)

        return agcg_cleaned


# the group of cards held by a player. used for operations dealing with another player's hand and/or the game object.
class GinHand(GinCardGroup):
    def __init__(self):
        GinCardGroup.__init__(self)

    # compare our hand against another hand and modify our hand in place, removing all cards that have been layed off
    def process_layoff(self, knocking_hand):
        """@type knocking_hand: GinHand"""

        # get a list of our deadwood cards
        gcg_deadwood = self.deadwood_cards()

        agcg_knocker_sets = knocking_hand.enumerate_all_sets()
        agcg_knocker_melds = knocking_hand.enumerate_all_melds()

        # We will lay off against our opponent's sets.

        # for each deadwood card we hold:
        for c in gcg_deadwood:
            # for each set held by knocker:
            for gcg in agcg_knocker_sets:
                # if our rank matches knocker's rank, we lay it off
                if gcg.cards[0].rank == c.rank:
                    self.discard(c)

        # We will attempt to lay off each card twice. In the case that we have two connected cards that will layoff on
        # the same meld (for instance: we hold 4c5c, knocker holds Ac2c3c) we cannot lay off the 5c until we first lay
        # off the 4c. Sorting does not necessarily fix this, as we may lay off low first or high first. Therefore,
        # we run the process twice. We do not run the process a third time, as that would imply we held a 3-card meld
        # of our own (which would not count as deadwood).

        for i in range(2):
            # for each deadwood card we hold:
            for c in gcg_deadwood:
                # for each meld held by knocker:
                for gcg in agcg_knocker_melds:
                    # if our suit matches the meld's suit:
                    if c.suit == gcg.cards[0].suit:
                        # if our rank is one less than the lowest rank of the meld, we lay it off
                        if c.rank == gcg.cards[0].rank - 1:
                            self.discard(c)
                        # if our rank is one more than the highest of the meld, we lay it off
                        elif c.rank == gcg.cards[-1].rank + 1:
                            self.discard(c)
