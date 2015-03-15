#!/usr/bin/python
#
# gin.py
#
# 2014/01/18
# rg
#
# base classes for gin rummy

from deck import *
from operator import attrgetter, itemgetter
from gindeck import *


# card organization and management. takes as input an array of card tuples. maintains objects internally as GinCards
class GinCardGroup():
    def __init__(self, card_list=None):
        self.cards = []
        if card_list is not None:
            for card_tuple in card_list:
                self.add(card_tuple[0], card_tuple[1])

    # add a card by value. guarantee sort.
    def add(self, rank, suit):
        self.cards.append(GinCard(rank, suit))
        self.sort()

    # add a card by copy. guarantee sort.
    def add_card(self, card):
        self.cards.append(card)
        self.sort()

    # remove a Card
    def remove(self, requested):
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

    # Card-wrapper for contains()
    def contains_card(self, card):
        return self.contains(card.rank, card.suit)

    def size(self):
        count = 0
        for _ in self.cards:
            count += 1
        return count

    def sum_points(self):
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

        # for aces we must have A23
        if card.rank == 1:    # Ace
            if self.contains(2, card.suit) and self.contains(3, card.suit):
                return True
            else:
                return False

        # for deuces we can have A23 or 234
        elif card.rank == 2:  # 2
            if self.contains(1, card.suit) and self.contains(3, card.suit):
                return True
            elif self.contains(3, card.suit) and self.contains(4, card.suit):
                return True
            else:
                return False

        # for kings we must have exactly JQK
        elif card.rank == 13:  # King
            if self.contains(11, card.suit) and self.contains(12, card.suit):
                return True
            else:
                return False

        # for queens we can have JQK or TJQ
        elif card.rank == 12:  # Queen
            if self.contains(11, card.suit) and self.contains(13, card.suit):
                return True
            elif self.contains(10, card.suit) and self.contains(11, card.suit):
                return True
            else:
                return False

        # for all other cards, we can have [card-2,card-1,card], [card-1,card,card+1] or [card,card+1,card+2]
        else:
            if self.contains(card.rank - 2, card.suit) and self.contains(card.rank - 1, card.suit):
                return True
            elif self.contains(card.rank - 1, card.suit) and self.contains(card.rank + 1, card.suit):
                return True
            elif self.contains(card.rank + 1, card.suit) and self.contains(card.rank + 2, card.suit):
                return True
            else:
                return False

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
        all_melds = list()

        # First, check for 4-sets
        if self.size() > 3:
            for c in self.cards:
                if self._is_in_a_4set(c):
                    quad_cards = []
                    for s in c.all_suits():
                        quad_cards.append((c.rank, s))

                    all_melds.append([quad_cards[0], quad_cards[1], quad_cards[2], quad_cards[3]])

                    # When a 4-card set is found, also add all 4 of the possible 3-card melds
                    all_melds.append([quad_cards[0], quad_cards[1], quad_cards[2]])
                    all_melds.append([quad_cards[1], quad_cards[2], quad_cards[3]])
                    all_melds.append([quad_cards[2], quad_cards[3], quad_cards[0]])
                    all_melds.append([quad_cards[3], quad_cards[0], quad_cards[1]])
                # Next, check for 3-sets (reminder: here we check for 3sets exclusive of 4sets)
                elif self._is_in_a_3set(c):
                    set_cards = [x for x in self.cards if x.rank == c.rank]
                    set_cards_list = map(lambda y: (y.rank, y.suit), set_cards)
                    all_melds.append(set_cards_list)

        # Next, check for 3-melds
        if self.size() > 2:
            self.sort(by_suit=True)
            for i in range(0, len(self.cards) - 3 + 1):
                first_card = self.cards[i]
                second_card = self.cards[i + 1]
                third_card = self.cards[i + 2]
                if first_card.suit == second_card.suit == third_card.suit:
                    if first_card.rank + 1 == second_card.rank and second_card.rank + 1 == third_card.rank:
                        all_melds.append([(first_card.rank, first_card.suit),
                                          (second_card.rank, second_card.suit),
                                          (third_card.rank, third_card.suit)])

        # Next, check for 4-melds
        if self.size() > 3:
            for i in range(0, len(self.cards) - 4 + 1):
                first_card = self.cards[i]
                second_card = self.cards[i + 1]
                third_card = self.cards[i + 2]
                fourth_card = self.cards[i + 3]
                if first_card.suit == second_card.suit == third_card.suit == fourth_card.suit:
                    if (first_card.rank + 1 == second_card.rank and
                            second_card.rank + 1 == third_card.rank and
                            third_card.rank + 1 == fourth_card.rank):
                        all_melds.append([(first_card.rank, first_card.suit),
                                          (second_card.rank, second_card.suit),
                                          (third_card.rank, third_card.suit),
                                          (fourth_card.rank, fourth_card.suit)])

        # Finally, check for 5-melds
        if self.size() > 4:
            for i in range(0, len(self.cards) - 5 + 1):
                first_card = self.cards[i]
                second_card = self.cards[i + 1]
                third_card = self.cards[i + 2]
                fourth_card = self.cards[i + 3]
                fifth_card = self.cards[i + 4]
                if first_card.suit == second_card.suit == third_card.suit == fourth_card.suit == fifth_card.suit:
                    if (first_card.rank + 1 == second_card.rank and
                            second_card.rank + 1 == third_card.rank and
                            third_card.rank + 1 == fourth_card.rank and
                            fourth_card.rank + 1 == fifth_card.rank):
                        all_melds.append([(first_card.rank, first_card.suit),
                                          (second_card.rank, second_card.suit),
                                          (third_card.rank, third_card.suit),
                                          (fourth_card.rank, fourth_card.suit),
                                          (fifth_card.rank, fifth_card.suit)])

        # de-dupe. O(n^2) but small population so whatever.
        all_melds_cleaned = list()
        for m in all_melds:
            if m not in all_melds_cleaned:
                all_melds_cleaned.append(m)

        # sort each meld by rank,suit
        for m in all_melds_cleaned:
            m.sort(key=itemgetter(0, 1))

        # return a sorted array of GinCardGroups, one containing each meld
        all_melds_cleaned.sort()
        gin_card_groups  = []
        for meld in all_melds_cleaned:
            gin_card_groups.append(GinCardGroup(meld))

        return gin_card_groups


# the group of cards held by a player
class GinHand:
    def __init__(self):
        self.cg = GinCardGroup()

    # add a card by rank and suit
    def add(self, rank, suit):
        self.cg.add(rank, suit)

    # add a Card, then sort the hand
    def add_card(self, card):
        self.cg.add_card(card)

    # discard a card
    def discard(self, gincard):
        if gincard in self.cg.cards:
            self.cg.remove(gincard)

    def _sort_hand(self, by_suit=False):
        self.cg.sort(by_suit)

    def size(self):
        return self.cg.size()

    # return card at specific index (0-10)
    def get_card_at_index(self, index):
        if index > 10 or index < 0:
            raise Exception
        else:
            return self.cg.cards[index]

    # return total points for this hand
    def points(self):
        return self.cg.sum_points()

    # return a list of all possible melds (not sets) that use a particular card
    @staticmethod
    def _melds_using_this_card(card):

        return_melds = []
        all_possible_melds = []

        # generate a list of all possible melds
        for s in Card.all_suits():
            # add all 3-card melds
            for _ in range(1, 12):
                all_possible_melds.append(((_, s), (_ + 1, s), (_ + 2, s)))
                # add all 4-card melds
            for _ in range(1, 11):
                all_possible_melds.append(((_, s), (_ + 1, s), (_ + 2, s), (_ + 3, s)))
                # add all 5-card melds
            for _ in range(1, 10):
                all_possible_melds.append(((_, s), (_ + 1, s), (_ + 2, s), (_ + 3, s), (_ + 4, s)))

        # for each meld, check to see if this card is in it. if so, mark it for return.
        for m in all_possible_melds:
            if (card.rank, card.suit) in m:
                return_melds.append(m)

        return sorted(return_melds, key=itemgetter(0, 1))

    def _contains_card(self, rank, suit):
        return self.cg.contains(rank, suit)

    # Given an array of GinCardGroups as melds, we return all melds not containing card from a given GinCardGroup.
    # This allows us to reduce the list of melds we are interested in exploring.
    @staticmethod
    def _prune_meld_group(melds, pruner_meld):

        # if we're given an empty base_meld to prune with, don't do any pruning
        if len(pruner_meld.cards) == 0:
            return melds

        pruned = []
        for meld in melds:
            for card in pruner_meld.cards:
                # test for the presence of card in meld
                if meld.contains_card(card):
                    break

                # record meld, preventing duplicates
                if meld not in pruned:
                    pruned.append(meld)

        return pruned

    def deadwood_count(self):
        debug_func = False
        # begin with worst case: entire hand is deadwood.
        worst_case = self.points()

        # optimization step: we remove all cards not part of a set or a meld
        specimen = GinCardGroup()
        early_deadwood = GinCardGroup()
        for card in self.cg.cards:
            if self.cg._is_in_a_meld(card) or self.cg._is_in_a_3set(card) or self.cg._is_in_a_4set(card):
                specimen.add(card.rank, card.suit)
            else:
                early_deadwood.add_card(card)

        if debug_func:
            print "early_deadwood: " + str(early_deadwood.sum_points())
            all_melds = specimen.enumerate_all_melds_and_sets()
            print "all_melds:"
            for meld in all_melds:
                print '\t' + ''.join((x.to_s() + '\t') for x in meld.cards)

        # recursion. add smallest discovered deadwood count to early_deadwood count
        explored_case = self._examine_melds(specimen) + early_deadwood.sum_points()

        lowest_deadwood = min(worst_case, explored_case)

        if debug_func:
            print "lowest_deadwood: " + str(lowest_deadwood)

        return lowest_deadwood

    # our recursive call
    # parameters:
    #   cg          a GinCardGroup, representing cards to examine
    def _examine_melds(self, cg, indent_level=0):
        debug_func = False
        if debug_func:
            print ''.join('\t' for x in range(0, indent_level)) + "examine_melds[d=" + str(indent_level) + "]: " +\
                  ''.join((str(x.to_s()) + '\t') for x in cg.cards)

        # no cards means we're holding zero deadwood.
        if cg.size() == 0:
            return 0

        # holding 1 or 2 cards means we're holding pure deadwood. return the sum.
        if cg.size() < 3:
            return sum(card.rank for card in cg.cards)

        # enumeration step: generate all melds possible from our specimen
        all_melds = cg.enumerate_all_melds_and_sets()

        # ceiling is case where entire hand is deadwood (note that this is only for the subset cg, not a 10 card hand)
        minimum_deadwood = cg.sum_points()

        # The recursion. One by one, we enumerate through all possible meld combinations we can make using this subset
        #  of cards, tracking the lowest deadwood value.
        for excluded_meld in all_melds:
            if debug_func:
                print ''.join('\t' for x in range(0, indent_level+1)) + "excluded meld: " +\
                      ''.join((str(x.to_s()) + '\t') for x in excluded_meld.cards)

            # create a list of cards to examine, excluding cards in the excluded_meld
            cards_to_examine = GinCardGroup()
            for card in cg.cards:
                for excluded_card in excluded_meld.cards:
                    if card.rank != excluded_card.rank and card.suit != excluded_card.suit:
                        cards_to_examine.add_card(card)
                        break

            # recursive call
            result = self._examine_melds(cards_to_examine, indent_level+1)

            if debug_func:
                print ''.join('\t' for x in range(0, indent_level+1)) + "deadwood: " + str(result) + "\n"

            # track lowest deadwood
            minimum_deadwood = min(minimum_deadwood, result)


        return minimum_deadwood