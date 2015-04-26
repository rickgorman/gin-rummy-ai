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
        self.gene_size = 4000
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


import signal
import sys


class RunCheckIntelligence(object):
    def __init__(self):

        self.register_sigint()
        self.exhibit_winners = True

        self.population_size = 9
        self.gene_size = 4000
        self.max_generations = int(20 * 60 * 24)  # one day of runtime: runs about 20 per minute

        local_storage = 'playground_check_intelligence.persist.txt'

        self.p = Population(self.gene_size, self.population_size, retain_best=3, local_storage=local_storage)
        self.p.persist(action='load')
        self.p.retain_best = 4

        self.register_sigint()

    def run(self):
        for _ in range(self.max_generations):
            self.p.generate_next_generation()

        self.p.persist(action='store')

        if exhibit_winners:
            self.do_exhibit_winners()

    def do_exhibit_winners(self):
        # get top two and watch a couple games
        best_genes = self.p.get_top_members(2)

        p2 = Population(4000, 2)
        p2.member_genes = {}
        p2.add_member(best_genes[0], 0)
        p2.add_member(best_genes[1], 0)

        utility.enable_logging_debug = True
        utility.enable_logging_info = True

        p2.fitness_test()

    def register_sigint(self):
        the_class = self

        def signal_handler(the_signal, frame):
            print('\nCaught Ctrl-C. Storing population...')
            the_class.p.persist(action='store')
            print('population stored. Quitting.')

            if the_class.exhibit_winners:
                the_class.do_exhibit_winners()

            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)


for _ in range(1):
    a = RunCheckIntelligence()
    a.run()