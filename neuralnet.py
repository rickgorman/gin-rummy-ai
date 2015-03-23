#!/usr/bin/python
#
# neuralnet.py
#
# 2014/01/18
# rg
#
# base neural networking classes


# Notes:
# - we can grow one net for normal play and a second net for handling the invalid knock scenario

class Neuron:
    def __init__(self):
        self.dendrite_tree = []
        self.axon = None

    # connect this neuron to the dendrite tree of target neuron
    def attach_my_axon(self, target):
        self.axon = target
        target.attach_my_dendrite(self)

    # connect a neuron to our dendrite tree
    def attach_my_dendrite(self, target):
        if self not in target.dendrite_tree:
            self.dendrite_tree.append(target)
