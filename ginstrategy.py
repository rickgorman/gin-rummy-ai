#!/usr/bin/python
#
# ginstrategy.py
#
# 2014/08/8
# rg
#
# base classes for gin rummy strategy

# The GinStrategy class needs to be aware of the following (via visitor patterns):
# - discard pile
# - inquiring player's hand
# - list of actions taken thus far in the current game

class GinStrategy:
    def __init__(self):
        pass

    def best_action(self):
        pass


class MockGinStrategy(GinStrategy):
    def __init__(self, mockaction=None):
        GinStrategy.__init__(self)
        if mockaction is None:
            self.action = ['DISCARD', 0]
        else:
            self.action = mockaction

    def best_action(self,):
        # by default, we discard the first card
        return self.action