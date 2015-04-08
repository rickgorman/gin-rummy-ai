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

import math


class GinStrategy(object):
    def __init__(self, us, opponent, ginmatch):
        self.us = us
        self.opponent = opponent
        self.ginmatch = ginmatch
        assert us != opponent, "we can't play against ourselves"

    def determine_best_action(self):
        pass


class NeuralGinStrategy(GinStrategy):
    def __init__(self, us, opponent, ginmatch, neural_net):
        super(NeuralGinStrategy, self).__init__(us, opponent, ginmatch)

        # ensure we have a neural net with our expected outputs
        self.nn = neural_net
        required_outputs = ['action', 'index', 'accept_improper_knock']
        for output in required_outputs:
            assert output in self.nn.outputs.keys(), "we require a neural net with an '" + output + "' output neuron"

    def consider_accepting_improper_knock(self):
        self.nn.pulse()
        return self.nn.outputs['accept_improper_knock']

    # split a given a signal in [0, 1] into n buckets, returning the index of the bucket (starting at 1)
    @staticmethod
    def decode_signal(signal, buckets):
        if signal == 1:
            return buckets - 1
        else:
            return int(float(signal) * float(buckets))

    # step function for the output neuron
    def decode_best_action(self):
        actions = ['DISCARD', 'DRAW', 'KNOCK', 'KNOCK-GIN', 'PICKUP-FROM-DISCARD']

        index = NeuralGinStrategy.decode_signal(self.nn.outputs['action'], len(actions))

        return actions[index]