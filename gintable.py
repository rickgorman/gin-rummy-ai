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


class GinTable(Observable):
    def __init__(self):
        super(GinTable, self).__init__()
        self.player1 = False
        self.player2 = False

        # on instantiation, create a new, shuffled deck
        self.deck = GinDeck()

        # also create a discard pile
        self.discard_pile = []

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

    def organize_data(self):
        data = {}

        # we start with the deck cards. data[0] holds the bottom card of the deck. we pad data[] with 0's once we
        #   run out of cards to ensure we return 52 items for the deck
        deck_size = len(self.deck.cards)
        for i in range(deck_size):
            data[i] = self.deck.cards[i].ranking()
        for i in range(deck_size, 52):
            data[i] = 0

        # we do the same for the discard pile. the bottommost card is loaded first.
        discard_size = len(self.discard_pile)
        for i in range(deck_size, deck_size + discard_size):
            data[i] = self.discard_pile[i-deck_size].ranking()
        for i in range(deck_size + discard_size, 104):
            data[i] = 0

        return data


class TableSeatingError(Exception):
    pass