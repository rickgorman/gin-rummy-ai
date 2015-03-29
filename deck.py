#!/usr/bin/python
#
# deck.py
#
# 2014/01/18
# rg
#
# base classes for managing a deck of cards

from random import shuffle


class Card:
    # create a new card with given rank and suit. A=1, J=11, Q=12, K=13
    def __init__(self, rank, suit):
        # sanity checks
        if rank < 1 or rank > 13:
            raise(AttributeError("rank out of range: %d" % rank))
        if suit not in ['c', 'h', 'd', 's']:
            raise(AttributeError("suit not valid: %s" % suit))

        self.rank = rank
        self.suit = suit

    @staticmethod
    def all_suits():
        return ['c', 'h', 'd', 's']

    # compare by rank. if equal, then compare by suit
    def __cmp__(self, other):

        suit_rankings = ['c', 'd', 'h', 's']

        r = self.rank.__cmp__(other.rank)
        # if rank is equal
        if not r:
            return suit_rankings.index(self.suit) - suit_rankings.index(other.suit)
        else:
            return r


class Deck(object):
    def __init__(self):
        self.cards = []
        for suit in ('c', 'd', 'h', 's'):
            for rank in range(1, 14):
                c = Card(rank, suit)
                self.cards.append(c)
        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

    def deal_a_card(self):
        return self.cards.pop()