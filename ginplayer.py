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
from observer import *


# handle invalid draws
class DrawException(Exception):
    pass


# handle invalid strategies
class StrategyExecutionException(Exception):
    pass


# the player
class GinPlayer(Observable):
    # begin with empty hand
    def __init__(self, strategy=False):
        super(GinPlayer, self).__init__()
        # parameter passing
        self.strategy = strategy

        self.action = False

        self.table = False

        self.id = int(random() * 2 ** 128)  # guid
        self.hand = GinHand()

        self._knock_listeners = []
        self._knock_gin_listeners = []

    # listen for knocks
    def register_knock_listener(self, listener):
        if not listener in self._knock_listeners:
            self._knock_listeners.append(listener)

    def notify_knock_listeners(self):
        for listener in self._knock_listeners:
            listener.notify_of_knock(self)

    # discard one card and knock
    def knock(self, card):
        self.discard_card(card)
        self.notify_knock_listeners()

    # listen for gins
    def register_knock_gin_listener(self, listener):
        if not listener in self._knock_gin_listeners:
            self._knock_gin_listeners.append(listener)

    def notify_knock_gin_listeners(self):
        for listener in self._knock_gin_listeners:
            listener.notify_of_knock_gin(self)

    # discard one card and knock
    def knock_gin(self, card):
        self.discard_card(card)
        self.notify_knock_gin_listeners()

    # sit at a table
    def sit_at_table(self, table):
        if table.seat_player(self):
            self.table = table

    # add the given card to this player's hand
    @notify_observers  # here mostly to satisfy unit tests
    def _add_card(self, card):
        self.hand.add_card(card)

    # implement the Observable criteria. return a dict of ints representing our hand. key corresponds to hand.cards idx
    def organize_data(self):
        indexes = range(len(self.hand.cards))
        rankings = [c.ranking() for c in self.hand.cards]
        return dict(zip(indexes, rankings))

    def draw(self):
        if self.hand.size() == 11:
            raise DrawException
        else:
            card = self.table.deck.deal_a_card()
            self.hand.add_card(card)
            return card

    def consult_strategy(self):
        self.action = self.strategy.best_action()

    # here we act on the advice we received from the strategy
    @notify_observers
    def execute_strategy(self):
        if not self.action:
            raise StrategyExecutionException('no action to execute!')
        else:
            if self.action[0] == 'DRAW':
                self.draw()
            elif self.action[0] == 'PICKUP-DISCARD':
                self.pickup_discard()
            elif self.action[0] == 'DISCARD':
                index = self.action[1]
                card = self.hand.get_card_at_index(index)
                self.discard_card(card)
            elif self.action[0] == 'KNOCK':
                index = self.action[1]
                card = self.hand.get_card_at_index(index)
                self.knock(card)
            elif self.action[0] == 'KNOCK-GIN':
                index = self.action[1]
                card = self.hand.get_card_at_index(index)
                self.knock_gin(card)

    # consult the strategy and perform the action suggested
    def take_turn(self):
        # if we have 11 cards, we do this once. otherwise, we do it twice.
        if self.hand.size() == 11:
            self.consult_strategy()
            self.execute_strategy()
        elif self.hand.size() == 10:
            self.consult_strategy()
            self.execute_strategy()
        else:
            raise Exception('not enough cards in hand to take a turn')

    def pickup_discard(self):
        card = self.table.discard_pile.pop()
        self._add_card(card)
        return card

    # drop the given card into the discard pile
    def discard_card(self, card):
        try:
            self.hand.discard(card)
            self.table.discard_pile.append(card)
        except ValueError:
            raise Exception("card not in our hand")
        except AttributeError:
            raise Exception("cards not behaving like a list: " + AttributeError.message)
        return card