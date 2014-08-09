#!/usr/bin/python
#
# gintable.py
#
# 2014/08/08
# rg
#
# base classes for gin rummy table

from ginplayer import *


class GinTable:
    def __init__(self):
        self.player1 = False
        self.player2 = False

    # seat a player at the table. take special care to not let the same player sit at the table twice.
    def seat_player(self, player):
        # if player is already sitting at this table, throw an error
        if (self.player1 is not False and self.player1.id == player.id) or \
           (self.player2 is not False and self.player2.id == player.id):
            raise TableSeatingError("player is already seated at table")
        # if p1's seat is empty, seat the player here
        elif not self.player1:
            self.player1 = player
            return True
        # if p2's seat is empty AND this player is not p1, seat the player here
        elif not self.player2:
            self.player2 = player
            return True
        else:
            raise TableSeatingError("gintable is full")


class TableSeatingError(Exception):
    pass