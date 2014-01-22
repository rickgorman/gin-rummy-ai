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
from operator import attrgetter


class GinCard:
    def __init__(self, card):
        self.card = card
        self.rank = card.rank
        self.suit = card.suit

        if self.rank < 10:
            self.point_value = self.rank
        else:
            self.point_value = 10


# the group of cards held by a player
class GinHand:
    def __init__(self):
        self.cards = []

    def enumerate_all_melds_and_sets(self):
        all_melds = []
        self.sort_hand()

        # First, check for 4 card melds of the same-numbered card
        for c in self.cards:
            # When a 4-card meld is found, also add all 4 of the possible 3-card melds
            if self._is_in_a_4set(c, self.cards):
                quad_cards = []
                for s in c.all_suits():
                    quad_cards.append((c.rank, s))

                all_melds.append([quad_cards[0], quad_cards[1], quad_cards[2], quad_cards[3]])

                all_melds.append([quad_cards[0], quad_cards[1], quad_cards[2]])
                all_melds.append([quad_cards[0], quad_cards[1], quad_cards[3]])
                all_melds.append([quad_cards[1], quad_cards[2], quad_cards[3]])
                all_melds.append([quad_cards[0], quad_cards[1], quad_cards[3]])


        # Next, check for 3 card melds of the same-numbered card
        for c in self.cards:
            if self._is_in_a_3set(c, self.cards):
                set_cards = [x for x in self.cards if x.rank == c.rank]
                all_melds.append(set_cards)

        # Next, check for 3 card melds in the same suit
        # Next, 4 card melds
        # Finally, 5 card melds

        # Lastly, sort each meld by suit. Then, sort all melds against one another.

        return all_melds

    # calculate and return deadwood
    def deadwood_count(self):
        pass

    # our recursive call
    def _deadwood_count(self, cards):
        pass

    @staticmethod
    def _is_in_a_meld(card, cards):
        # must have at least 3 cards to have a set
        if len(cards) < 3:
            return False

        # for aces we must have A23
        if card.rank == 1:    # Ace
            if self._contains_card(cards, 2, card.suit) and self._contains_card(cards, 3, card.suit):
                return True
            else:
                return False

        # for deuces we can have A23 or 234
        elif card.rank == 2:  # 2
            if   self._contains_card(cards, 1, card.suit) and self._contains_card(cards, 3, card.suit):
                return True
            elif self._contains_card(cards, 3, card.suit) and self._contains_card(cards, 4, card.suit):
                return True
            else:
                return False

        # for kings we must have exactly JQK
        elif card.rank == 13:  # King
            if self._contains_card(cards, 11, card.suit) and self._contains_card(cards, 12, card.suit):
                return True

        # for queens we can have JQK or TJQ
        elif card.rank == 12:  # Queen
            if   self._contains_card(cards, 11, card.suit) and self._contains_card(cards, 13, card.suit):
                return True
            elif self._contains_card(cards, 10, card.suit) and self._contains_card(cards, 11, card.suit):
                return True
            else:
                return False

        # for all other cards, we can have [card-2,card-1,card], [card-1,card,card+1] or [card,card+1,card+2]
        else:
            if   self._contains_card(cards, card.rank - 2, card.suit) and self._contains_card(cards, card.rank - 1,
                                                                                              card.suit):
                return True
            elif self._contains_card(cards, card.rank - 1, card.suit) and self._contains_card(cards, card.rank + 1,
                                                                                              card.suit):
                return True
            elif self._contains_card(cards, card.rank + 1, card.suit) and self._contains_card(cards, card.rank + 2,
                                                                                              card.suit):
                return True
            else:
                return False

    @staticmethod
    def _contains_card(cards, rank, suit):
        if any(c.rank == rank and c.suit == suit for c in cards):
            return True
        else:
            return False

    # determine if a card is part of a three-of-a-kind
    def _is_in_a_3set(self, card, cards):
        self.sort_hand()
        # we need to find exactly two other cards of the same rank
        matches = [x for x in cards if x.rank == card.rank and x.suit != card.suit]
        if len(matches) == 2:
            return True
        else:
            return False

    # determine if a card is part of a four-of-a-kind
    @staticmethod
    def _is_in_a_4set(card, cards):
        # we need to find at least two other cards of the same rank
        matches = [x for x in cards if x.rank == card.rank and x.suit != card.suit]
        if len(matches) == 3:
            return True
        else:
            return False


    # add a card, then sort the hand
    def add_card(self, card):
        self.cards.append(card)
        self.sort_hand()

    def discard(self):
        pass

    def sort_hand(self):
        self.cards.sort(key=attrgetter('rank', 'suit'))



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
