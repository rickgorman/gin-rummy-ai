#!/usr/bin/python
#
# gintable.py
#
# 2014/08/08
# rg
#
# base classes for gin rummy table. helps us sit correct arrangement of players.

from ginplayer import *
from gindeck import *
from observer import *
from utility import *
from pylru import lrudecorator
import line_profiler


class GinTable(Observable):
    def __init__(self):
        super(GinTable, self).__init__()
        self.player1 = False
        self.player2 = False

        # on instantiation, create a new, shuffled deck
        self.deck = GinDeck()

        # also create a discard pile
        self.discard_pile = []

        # we have 33 interesting points to export: 32 discards + size of deck
        self.observable_width = 33

    def __repr__(self):
        its_repr = "<gintable.GinTable object at " + hex(id(self)) + ">"
        its_repr += " height:" + str(len(self.deck.cards))
        its_repr += " discard_pile:" + str(self.discard_pile)
        return its_repr

    # seat a player at the table. take special care to not let the same player sit at the table twice.
    def seat_player(self, player):
        # if player is already sitting at this table, throw an error
        if (self.player1 is not False and self.player1.id == player.id) or \
           (self.player2 is not False and self.player2.id == player.id):
            raise TableSeatingError("player is already seated at table")
        # if p1's seat is empty, seat the player here
        elif not self.player1:
            self.player1 = player
            self.player1.table = self
            return True
        # if p2's seat is empty AND this player is not p1, seat the player here
        elif not self.player2:
            self.player2 = player
            self.player2.table = self
            return True
        else:
            raise TableSeatingError("gintable is full")

    @memoized(1)
    def organize_data(self):
        # we start with the current height of the drawing deck
        data = {0: len(self.deck.cards)}

        # we now add on the discard pile
        for i in range(len(self.discard_pile)):
            data[i] = self.discard_pile[i].ranking()

        # we then add 0's up to 32 possible discards -- 32 = 52 - 10(cards per hand) X 2(hands)
        discard_size = len(self.discard_pile)
        for i in range(1, discard_size):
            data[i] = self.discard_pile[i-1].ranking()
        for i in range(discard_size, 1+32):
            data[i] = 0

        return data

    @notify_observers_after
    def refresh_deck(self):
        self.deck = GinDeck()
        self.discard_pile = []

    # pop a card from the deck and return it
    @notify_observers_after
    def deal_a_card(self):
        card = self.deck.deal_a_card()
        return card

    @notify_observers_after
    def add_card_to_discard_pile(self, card):
        """ @type card: Card """
        self.discard_pile.append(card)

    # pop a card from the discard pile and return it
    @notify_observers_after
    def pickup_from_discard_pile(self):
        try:
            card = self.discard_pile.pop()
        except IndexError:
            raise InvalidPlayError("tried to pickup on the first move (with 11 cards)")
        return card


class TableSeatingError(Exception):
    pass


class InvalidPlayError(Exception):
    pass