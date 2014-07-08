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
