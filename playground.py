#!/usr/bin/python
#
# playground.py
#
# 2014/01/18
# rg
#
# test bed for gin rummy neural network

from genetic_algorithm import *


class Runner(object):
    def __init__(self):
        self.population_size = 4
        self.gene_size = 2000
        self.p = Population(self.gene_size, self.population_size)

        self.p.members = {}
        for _ in range(self.population_size):
            self.p.add_member(GeneSet(self.gene_size), 0)

        # run the fitness test and ensure one member has a win, and one has a loss
        self.p.fitness_test()

for _ in range(4):
    Runner()