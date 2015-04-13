#!/usr/bin/python
#
# playground.py
#
# 2014/01/18
# rg
#
# test bed for gin rummy neural network

from genetic_algorithm import *
from utility import *
import utility


class Runner(object):
    def __init__(self):
        self.population_size = 20
        self.gene_size = 2000
        self.p = Population(self.gene_size, self.population_size)

        for _ in range(10):
            self.p.generate_next_generation()

        # get top two and watch a couple games
        best_genes = self.p.get_top_members(2)

        self.p2 = Population(2000, 2)
        self.p2.member_genes = {}
        self.p2.add_member(best_genes[0], 0)
        self.p2.add_member(best_genes[1], 0)

        disable_logging_debug = False
        disable_logging_info = False

        self.p2.fitness_test()


class RunCheckIntelligence(object):
    def __init__(self):
        self.population_size = 12
        self.gene_size = 2000
        self.p = Population(self.gene_size, self.population_size, retain_best=4)

        for _ in range(10):
            self.p.generate_next_generation()

        # get top two and watch a couple games
        best_genes = self.p.get_top_members(2)

        self.p2 = Population(2000, 2)
        self.p2.member_genes = {}
        self.p2.add_member(best_genes[0], 0)
        self.p2.add_member(best_genes[1], 0)

        utility.enable_logging_debug = True
        utility.enable_logging_info = True

        self.p2.fitness_test()


for _ in range(1):
    a = RunCheckIntelligence()