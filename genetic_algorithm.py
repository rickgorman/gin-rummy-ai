#!/usr/bin/python
#
# genetic_algorithm.py
#
# 2015/04/08
# rg
#
# everything required to create a population, perform cross-overs and mutations and run fitness tests

import random
from texttable import *
from utility import *


class GeneSet(object):
    def __init__(self, genes=None):
        if isinstance(genes, int):
            # create genome of the requested size with random values in [0,1]
            self.genes = []
            default_length = genes
            [self.genes.append(random.random()) for _ in range(default_length)]
        elif isinstance(genes, list):
            # store genome, ensuring genes are valid
            for gene in genes:
                assert isinstance(gene, float)
                assert 0 <= gene <= 1, "gene is not within [0,1]: {1}".format(gene)
            self.genes = genes
        else:
            raise AssertionError("strange value passed in")

    @staticmethod
    def make_geneset(*args, **kwargs):
        return GeneSet(*args, **kwargs)

    # cross the genes of two GeneSets (sexy times)
    def cross(self, partner):
        # return a new GeneSet with length of longest genome
        child = self.make_geneset(max(len(self.genes), len(partner.genes)))

        # cross up to the length of the smallest partner's genome
        big_partner, small_partner = self, partner
        if len(self.genes) < len(partner.genes):
            big_partner, small_partner = partner, self

        # do the cross
        for i in range(len(small_partner.genes)):
            if int(random.random()*2) == 0:
                child.genes[i] = small_partner.genes[i]
            else:
                child.genes[i] = big_partner.genes[i]

        return child

    # destructively mutate our genes (independently) at a given probability
    def mutate(self, probability):
        for i in range(len(self.genes)):
            if random.random() > 1 - probability:
                self.genes[i] = random.random()


class GinGeneSet(GeneSet):
    def __init__(self, genes=None):
        super(GinGeneSet, self).__init__(genes)

    @staticmethod
    def make_geneset(*args, **kwargs):
        return GinGeneSet(*args, **kwargs)


class Population(object):
    def __init__(self, gene_size, population_size):
        self.members = {}
        self.current_generation = 0

        # create the initial genes
        for i in range(population_size):
            self.members[GeneSet(gene_size)] = {'wins': 0, 'losses':0, 'generation': 0}

    def draw(self):
        # Table 1: print leaderboard
        input_table = Texttable()
        input_table.set_deco(Texttable.HEADER | Texttable.BORDER)
        rows = []
        data_rows = []

        # header row
        rows.append(["ranking", "win rate (%)", "number of wins", "number of losses", "generation"])

        # gather data on our population
        for key in self.members.keys():
            wins, losses = self.members[key]['wins'], self.members[key]['losses']
            try:
                winrate = round(float(wins) / float(wins + losses), 3) * 100
                break
            except ZeroDivisionError:
                winrate = 0.000

            generation = self.members[key]['generation']
            data_rows.append([winrate, wins, losses, generation])

        # sort by winrate
        data_rows.sort(key=itemgetter(0), reverse=True)

        # collect the top 10 rankings
        for i in range(11):
            rows.append([i+1, data_rows[i][0], data_rows[i][1], data_rows[i][2], data_rows[i][3]])
        input_table.add_rows(rows[:11])

        print "\n" + "                     LEADERBOARD FOR GENERATION #{0}".format(str(self.current_generation))
        print input_table.draw()
