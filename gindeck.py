
#!/usr/bin/python
#
# gindeck.py
#
# 2014/08/09
# rg
#
# child classes for managing a deck specifically for Gin

from deck import *


class GinCard(Card):
    def __init__(self, rank, suit):
        Card.__init__(self, rank, suit)

        if self.rank < 10:
            self.point_value = self.rank
        else:
            self.point_value = 10

    def __repr__(self):
        return str(self.rank) + self.suit

    def to_s(self):
        return str(self.rank) + self.suit


class GinDeck(Deck):
    # deal out GinCards, rather than base Cards
    def deal_a_card(self):
        card = super(GinDeck, self).deal_a_card()
        return GinCard(card.rank, card.suit)