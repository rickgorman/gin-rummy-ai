#!/usr/bin/python
#
# ginplayer.py
#
# 2014/01/18
# rg
#
# base classes for gin rummy player

from random import random
from ginhand import *
from ginstrategy import *
from gintable import *


# the player
class GinPlayer:
    # begin with empty hand
    def __init__(self, strategy=False):
        # parameter passing
        self.strategy = strategy

        self.table = False

        self.id = int(random() * 2 ** 128)  # guid
        self.hand = GinHand()

        self._knock_listeners = []
        self._knock_gin_listeners  = []

    # listen for knocks
    def _register_knock_listener(self, listener):
        if not listener in self._knock_listeners:
            self._knock_listeners.append(listener)

    def _notify_knock_listeners(self):
        for listener in self._knock_listeners:
            listener.notify_of_knock(self)

    def knock(self):
        self._notify_knock_listeners()

    # listen for gins
    def _register_knock_gin_listener(self, listener):
        if not listener in self._knock_gin_listeners:
            self._knock_gin_listeners.append(listener)

    def _notify_knock_gin_listeners(self):
        for listener in self._knock_listeners:
            listener.notify_of_knock_gin(self)

    def knock_gin(self):
        self._notify_knock_gin_listeners()

    # sit at a table
    def _sit_at_table(self, table):
        try:
            if table.seat_player(self):
                self.table = table
        except FullTableError:
            raise RuntimeError("Table is full and so this player cannot be seated.")

    # add the given card to this player's hand
    def _add_card(self, card):
        self.hand.add_card(card)

    def draw(self):
        pass

    def pickup_discard(self):
        pass

    # drop the given card
    def discard_card(self, card):
        try:
            self.hand.discard(card)
        except ValueError:
            raise Exception("card not in our hand")
        except AttributeError:
            raise Exception("cards not behaving like a list")
        return card
