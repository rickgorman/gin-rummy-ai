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
