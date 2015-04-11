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
        self.population_size = 2
        self.gene_size = 5000
        self.p = Population(self.gene_size, self.population_size)

        # run the fitness test and ensure one member has a win, and one has a loss
        self.p.fitness_test()

Runner()