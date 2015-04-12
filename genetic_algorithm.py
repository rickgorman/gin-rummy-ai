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
from ginmatch import *
from neuralnet import *
from ginstrategy import *

# static seed for repeatability
random.seed(0)


class GeneSet(object):
    def __init__(self, genes=None):
        if isinstance(genes, int):
            # create genome of the requested size.
            # for the random seed values, we want to try to pick smart values.
            # let's make 2% of the weights significant and the rest small randoms
            self.genes = []
            default_length = genes
            possible_means = [0.0, 0.05, 0.1, 0.2]
            shuffle(possible_means)
            mean = possible_means[0]

            [self.genes.append(abs(random.gauss(0.3, 0.2))) for _ in range(int(0.02 * default_length))]
            [self.genes.append(abs(random.gauss(mean, 0.01))) for _ in range(int(0.98 * default_length))]
            shuffle(self.genes)

            # make sure the integer rounding doesn't lose us a gene or two
            for _ in range(genes - len(self.genes)):
                self.genes.append(abs(random.gauss(0.0, 0.01)))

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
            if int(random.random() * 2) == 0:
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
            self.add_member(GeneSet(gene_size), 0)

    # add a member with a given generation
    def add_member(self, geneset, generation):
        self.members[geneset] = {'wins': 0, 'losses': 0, 'generation': generation}

    # return the top N specimens of the population. our ranking method is as follows:
    #
    #                    number of wins
    #      ranking  =  -----------------
    #                  generations_lived
    #
    # the rationale here is that while we do want to retain elders who have done well in the past, we don't want
    # them to stick around due to a huge number of wins over a huge number of generations.
    def get_top_members(self, count):
        # see unutbu's answer at http://stackoverflow.com/questions/4690416
        top_list = sorted(self.members.items(),
                          key=lambda (k, v): v['wins'] / (v['generation'] + 1 - self.current_generation), reverse=True)

        top_list = top_list[:count]

        # separate out our keys
        top_keys = []
        [top_keys.append(top_list[i][0]) for i in range(len(top_list))]

        return top_keys

    # engage each member in competition with each other member, recording the results
    def fitness_test(self):
        already_tested = []
        for challenger_geneset in self.members:
            for defender_geneset in self.members:
                if challenger_geneset is not defender_geneset:
                    # do not test both A vs B AND B vs A. Just test them once.
                    if (challenger_geneset, defender_geneset) in already_tested or (
                        defender_geneset, challenger_geneset) in already_tested:
                        continue
                    already_tested.append((challenger_geneset, defender_geneset))

                    # create physical representations for these gene_sets
                    challenger_player = GinPlayer()
                    defender_player = GinPlayer()
                    log_debug("Testing: {0}  {1}".format(challenger_geneset, defender_geneset))

                    match = GinMatch(challenger_player, defender_player)
                    output_keys = ['action', 'index', 'accept_improper_knock']
                    num_inputs = 11 + 5 + 33
                    num_outputs = 3
                    num_hidden = int((num_inputs + num_outputs) * (2.0 / 3.0))

                    challenger_weightset = WeightSet(challenger_geneset, num_inputs, num_hidden, num_outputs)
                    defender_weightset = WeightSet(defender_geneset, num_inputs, num_hidden, num_outputs)

                    challenger_observers = [Observer(challenger_player), Observer(match.table), Observer(match)]
                    defender_observers = [Observer(defender_player), Observer(match.table), Observer(match)]

                    challenger_neuralnet = NeuralNet(challenger_observers, challenger_weightset, output_keys)
                    defender_neuralnet = NeuralNet(defender_observers, defender_weightset, output_keys)

                    challenger_strategy = NeuralGinStrategy(challenger_player, defender_player, match,
                                                            challenger_neuralnet)
                    defender_strategy = NeuralGinStrategy(defender_player, challenger_player, match,
                                                          defender_neuralnet)

                    challenger_player.strategy = challenger_strategy
                    defender_player.strategy = defender_strategy

                    winner = match.run()
                    #winner = challenger_player

                    if winner is challenger_player:
                        self.members[challenger_geneset]['wins'] += 1
                        self.members[defender_geneset]['losses'] += 1
                    elif winner is defender_player:
                        self.members[defender_geneset]['wins'] += 1
                        self.members[challenger_geneset]['losses'] += 1

    # remove members from prior generations, sparing the top N specimens
    def cull(self, survivor_count):
        # find the top N specimens
        survivor_list = sorted(self.members.items(), key=lambda (k, v): v['wins'], reverse=True)[:survivor_count]

        # separate our survivor keys
        survivor_keys = []
        [survivor_keys.append(survivor_list[i][0]) for i in range(len(survivor_list))]

        # the culling
        for key in self.members.keys():
            if key not in survivor_keys:
                del self.members[key]

    # breed the top N individuals against each other, sexually (no asexual reproduction)
    def cross_over(self, breeder_count):
        breeders = self.get_top_members(breeder_count)

        for breeder in breeders:
            for mate in breeders:
                # prevent asexual reproduction (this will cause result in clone wars)
                if mate is not breeder:
                    newborn = breeder.cross(mate)
                    self.add_member(newborn, self.current_generation + 1)

        # advance the generation counter
        self.current_generation += 1

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
            rows.append([i + 1, data_rows[i][0], data_rows[i][1], data_rows[i][2], data_rows[i][3]])
        input_table.add_rows(rows[:11])

        print "\n" + "                     LEADERBOARD FOR GENERATION #{0}".format(str(self.current_generation))
        print input_table.draw()
