#!/usr/bin/python
#
# gin.py
#
# 2014/01/18
# rg
#
# base classes for gin rummy

from deck import *
from random import random
from operator import attrgetter, itemgetter


class GinCard(Card):
    def __init__(self, rank, suit):
        Card.__init__(self, rank, suit)

        if self.rank < 10:
            self.point_value = self.rank
        else:
            self.point_value = 10


# the group of cards held by a player
class GinHand:
    def __init__(self):
        self.cards = []

    # add a card, then sort the hand
    def add_card(self, gincard):
        self.cards.append(gincard)
        self._sort_hand()

    # discard a card, if we are holding it
    def discard(self, gincard):
        if gincard in self.cards:
            self.cards.remove(gincard)

    def _sort_hand(self, by_suit=False):
        if by_suit:
            self.cards.sort(key=attrgetter('suit', 'rank'))
        else:
            self.cards.sort(key=attrgetter('rank', 'suit'))

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

    # check to see if a given card is in a meld that exists in this GinHand. Note that this handles 3, 4 and 5-melds
    #   as the latter varieties require the existence of the former in order to exist. We must have a 3-meld containing
    #   a 456 in order to have a 4-meld containing a 4567.
    def _is_in_a_meld(self, card):
        # must have at least 3 cards to have a set
        if len(self.cards) < 3:
            return False

        # for aces we must have A23
        if card.rank == 1:    # Ace
            if self._contains_card(2, card.suit) and self._contains_card(3, card.suit):
                return True
            else:
                return False

        # for deuces we can have A23 or 234
        elif card.rank == 2:  # 2
            if self._contains_card(1, card.suit) and self._contains_card(3, card.suit):
                return True
            elif self._contains_card(3, card.suit) and self._contains_card(4, card.suit):
                return True
            else:
                return False

        # for kings we must have exactly JQK
        elif card.rank == 13:  # King
            if self._contains_card(11, card.suit) and self._contains_card(12, card.suit):
                return True
            else:
                return False

        # for queens we can have JQK or TJQ
        elif card.rank == 12:  # Queen
            if self._contains_card(11, card.suit) and self._contains_card(13, card.suit):
                return True
            elif self._contains_card(10, card.suit) and self._contains_card(11, card.suit):
                return True
            else:
                return False

        # for all other cards, we can have [card-2,card-1,card], [card-1,card,card+1] or [card,card+1,card+2]
        else:
            if self._contains_card(card.rank - 2, card.suit) and self._contains_card(card.rank - 1, card.suit):
                return True
            elif self._contains_card(card.rank - 1, card.suit) and self._contains_card(card.rank + 1, card.suit):
                return True
            elif self._contains_card(card.rank + 1, card.suit) and self._contains_card(card.rank + 2, card.suit):
                return True
            else:
                return False

    def _contains_card(self, rank, suit):
        if any(c.rank == rank and c.suit == suit for c in self.cards):
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

    # return a list of lists of all melds and sets that can be built with the cards in this hand
    def enumerate_all_melds_and_sets(self):
        all_melds = list()
        self._sort_hand()

        # First, check for 4-sets
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
        self._sort_hand(by_suit=True)
        for i in range(0, 8):
            first_card = self.cards[i]
            second_card = self.cards[i + 1]
            third_card = self.cards[i + 2]
            if first_card.suit == second_card.suit == third_card.suit:
                if first_card.rank + 1 == second_card.rank and second_card.rank + 1 == third_card.rank:
                    all_melds.append([(first_card.rank, first_card.suit),
                                      (second_card.rank, second_card.suit),
                                      (third_card.rank, third_card.suit)])

        # Next, check for 4-melds
        for i in range(0, 7):
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
        for i in range(0, 6):
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

        # return a sorted list of all melds
        all_melds_cleaned.sort()
        return all_melds_cleaned

    def deadwood_count(self):

        # optimization step: we remove all cards not part of a set or a meld
        specimen = []
        early_deadwood = []
        for card in self.cards:
            if self._is_in_a_meld(card) or self._is_in_a_3set(card) or self._is_in_a_4set(card):
                specimen.append(card)
            else:
                early_deadwood.append(card)

        # last step: recursion, to determine which remaining cards are deadwood. add result to early_deadwood count
        return self._deadwood_count(specimen) + sum(card.rank for card in early_deadwood)

    # our recursive call
    def _deadwood_count(self, cards):

        #
        pass

# the player
class GinPlayer:
    # begin with empty hand
    def __init__(self):
        self.id = int(random() * 2 ** 128)  # guid
        self.hand = GinHand()
        self._knock_listeners = []

    # listen for knocks
    def _register_knock_listener(self, listener):
        if not listener in self._knock_listeners:
            self._knock_listeners.append(listener)

    def _notify_listeners(self):
        for listener in self._knock_listeners:
            listener.notify_of_knock(self)

    def knock(self):
        self._notify_listeners()

    # add the given card to its hand
    def add_card(self, card):
        self.hand.add_card(card)

    # drop the given card
    def discard_card(self, card):
        try:
            self.hand.discard(card)
        except ValueError:
            raise Exception("card not in our hand")
        except AttributeError:
            raise Exception("cards not behaving like a list")
        return card


# class to track physical elements of a gin game
class GinTable:
    def __init__(self):
        self.deck = None
        self.discard_pile = None


# class simulating a game between two players.
#
# Rules:
# 1) dealer gets 10 cards
# 2) eldest gets 11 cards
# 3) play begins with eldest discarding one card
# 4) play alternates until a player knocks (10 deadwood or less) or we run out of cards.
#    - if we run out of cards, we randomly pick a winner (to help eliminate GA infinite loops)
#    - if a player knocks with more than 10 deadwood, that player's hand is played open until end of game
#    - undercut bonus of 20 points, gin bonus of 20 points
#    - on valid gin: no layoffs.
#    - on valid knock: layoffs allowed.
# 5) player with least deadwood at end of game wins the game (no counting to 100 points, yet (TODO))

class GinGame:
    def __init__(self, p1, p2):
        # randomly seat players
        if random() > 0.5:
            self.player1 = p1
            self.player2 = p2
        else:
            self.player1 = p2
            self.player2 = p1

        self.deck = Deck()

    # handler for knock_listener in GinPlayer class
    def notify_of_knock(self, player):
        # if the knock
        pass

    # deal
    def deal(self):
        pass

    def play(self):
        pass
