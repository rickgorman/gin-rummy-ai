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


class GinCard:

    def __init__(self, card):
        self.card = card
        self.point_value = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            7: 7,
            8: 8,
            9: 9,
            10: 10,
            11: 10,
            12: 10,
            13: 10
        }.get(self.card.rank)
        self.rank = card.rank
        self.suit = card.suit


# the player
class GinPlayer:

    # begin with empty hand
    def __init__(self, game):
        self.id   = int(random() * 2**128)  # guid
        self.hand = []
        self.game = game
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
    def draw_card(self, card):
        self.hand.append(card)

    # drop the given card
    def discard_card(self, card):
        try:
            self.hand.remove(card)
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


# class simulating a game between two players
class GinGame:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.deck = Deck()

    # handler for knock_listener in GinPlayer class
    def notify_of_knock(self, player):
        pass

    def begin_game(self):
