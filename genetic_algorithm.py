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
import pickle


class GeneSet(object):
    def __init__(self, genes=None):
        if isinstance(genes, int):
            # create genome of the requested size.
#            # for the random seed values, we want to try to pick smart values.
#            # let's make 2% of the weights significant and the rest small randoms
            self.genes = []
            default_length = genes
#            possible_means = [-2.0, -1.0, 0.0, 1.0, 2.0]
#            shuffle(possible_means)
#            mean = possible_means[0]
            mean = 0
            stdev = 1

#            [self.genes.append(abs(random.gauss(0, 1))) for _ in range(int(0.02 * default_length))]
#            [self.genes.append(abs(random.gauss(mean, 0.25))) for _ in range(int(0.98 * default_length))]
            [self.genes.append(random.gauss(mean, stdev)) for _ in range(default_length)]
#            shuffle(self.genes)

            # make sure the integer rounding doesn't lose us a gene or two
            for _ in range(genes - len(self.genes)):
                self.genes.append(abs(random.gauss(mean, stdev)))

        elif isinstance(genes, list):
            # store genome, ensuring genes are valid
            for gene in genes:
                assert isinstance(gene, float)
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

    # additively mutate our genes (independently) at a given probability
    def mutate(self, probability=None):
        if probability is None:
            probability = 0.001
        for i in range(len(self.genes)):
            if random.random() > 1 - probability:
                self.genes[i] += random.gauss(0, 0.5)


class GinGeneSet(GeneSet):
    def __init__(self, genes=None):
        super(GinGeneSet, self).__init__(genes)

    @staticmethod
    def make_geneset(*args, **kwargs):
        return GinGeneSet(*args, **kwargs)


class Population(object):
    def __init__(self, gene_size, population_size, retain_best=None, local_storage=None):
        self.member_genes = {}
        self.current_generation = 0

        if retain_best is None:
            # by default, keep at least 2 and at most best 10%
            self.retain_best = max(2, int(len(self.member_genes) * 0.10))
        else:
            self.retain_best = retain_best

        # persistent storage location
        if local_storage is None:
            self.local_storage = False
        else:
            self.local_storage = local_storage

        # create the initial genes
        for i in range(population_size):
            self.add_member(GeneSet(gene_size), 0)

    # iterate through one generation
    def generate_next_generation(self):
        # test the current generation
        self.fitness_test()

        log_warn(self.draw())

        # cull the meek elders
        self.cull()

        self.cross_over(self.retain_best)

        self.current_generation += 1

    # add a member with a given generation
    def add_member(self, geneset, generation):
        self.member_genes[geneset] = {'match_wins': 0, 'match_losses': 0, 'game_wins': 0, 'coinflip_game_wins': 0,
                                      'game_losses': 0, 'game_points': 0, 'generation': generation}

    # return the top N specimens of the population
    def get_top_members(self, count):

        top_list = sorted(self.member_genes.items(), key=lambda (k, v): self.ranking_func(v), reverse=True)
        top_list = top_list[:count]

        # separate out our keys
        top_keys = []
        [top_keys.append(top_list[i][0]) for i in range(len(top_list))]

        return top_keys

    def ranking_func(self, gene_item):
        game_wins           = gene_item['game_wins']
        coinflip_game_wins  = gene_item['coinflip_game_wins']
        game_losses         = gene_item['game_losses']
        age                 = max(1, float(self.current_generation - gene_item['generation'] + 1))

        game_points         = gene_item['game_points']
        points_per_generation = game_points / age

        # the only behavior we want to award is winning without a coinflip
        real_wins           = float(game_wins - coinflip_game_wins)

        try:
            winrate = (float(real_wins) / float(real_wins + game_losses))
        except ZeroDivisionError:
            winrate = 0

#        return real_wins / age
#        return points_per_generation * (1.0 - float((age-1)/100.0))
        points_per_win = game_points / max(1, real_wins)
#        old_age_debuff = (1.0 - float((age-1)/100.0))
        old_age_debuff = 1
        winrate_factor = 100 * winrate
        return (points_per_win + winrate_factor) * old_age_debuff

    # engage each member in competition with each other member, recording the results
    def fitness_test(self):
        already_tested = []
        for challenger_geneset in self.member_genes:
            for defender_geneset in self.member_genes:
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
                    num_inputs = 11 + 5 + 33
                    num_outputs = 4
                    num_hidden = int((num_inputs + num_outputs) * (2.0 / 3.0))

                    challenger_weightset = WeightSet(challenger_geneset, num_inputs, num_hidden, num_outputs)
                    defender_weightset = WeightSet(defender_geneset, num_inputs, num_hidden, num_outputs)

                    challenger_observers = [Observer(challenger_player), Observer(match.table), Observer(match)]
                    defender_observers   = [Observer(defender_player), Observer(match.table), Observer(match)]

                    challenger_neuralnet = GinNeuralNet(challenger_observers, challenger_weightset)
                    defender_neuralnet   = GinNeuralNet(defender_observers,   defender_weightset)

                    challenger_strategy = NeuralGinStrategy(challenger_player, defender_player, match,
                                                            challenger_neuralnet)
                    defender_strategy = NeuralGinStrategy(defender_player, challenger_player, match,
                                                          defender_neuralnet)

                    challenger_player.strategy = challenger_strategy
                    defender_player.strategy = defender_strategy

                    match_result = match.run()
                    winner                      = match_result['winner']
                    challenger_wins             = match_result['p1_games_won']
                    challenger_wins_by_coinflip = match_result['p1_games_won_by_coinflip']
                    challenger_losses           = match_result['p1_games_lost']
                    defender_wins               = match_result['p2_games_won']
                    defender_wins_by_coinflip   = match_result['p2_games_won_by_coinflip']
                    defender_losses             = match_result['p2_games_lost']
                    winner_point_delta          = match_result['winner_point_delta']

                    assert challenger_wins_by_coinflip <= challenger_wins, "bad challenger wins"
                    assert defender_wins_by_coinflip   <= defender_wins,   "bad defender wins"

                    # track match wins
                    if winner is challenger_player:
                        self.member_genes[challenger_geneset]['game_points'] += winner_point_delta
                        self.member_genes[challenger_geneset]['match_wins'] += 1
                        self.member_genes[defender_geneset]['match_losses'] += 1
                    elif winner is defender_player:
                        self.member_genes[defender_geneset]['game_points'] += winner_point_delta
                        self.member_genes[defender_geneset]['match_wins']     += 1
                        self.member_genes[challenger_geneset]['match_losses'] += 1

                    # track game wins
                    self.member_genes[challenger_geneset]['game_wins']  += challenger_wins
                    self.member_genes[defender_geneset]['game_wins']      += defender_wins

                    # track coinflip wins
                    self.member_genes[challenger_geneset]['coinflip_game_wins'] += challenger_wins_by_coinflip
                    self.member_genes[defender_geneset]['coinflip_game_wins']   += defender_wins_by_coinflip

                    # track game losses
                    self.member_genes[challenger_geneset]['game_losses'] += challenger_losses
                    self.member_genes[defender_geneset]['game_losses']     += defender_losses

    # remove members from prior generations, sparing the top N specimens
    def cull(self):
        # find the top N specimens
        survivor_list = self.get_top_members(self.retain_best)

        # the culling
        for key in self.member_genes.keys():
            if key not in survivor_list:
                del self.member_genes[key]

    # breed the top N individuals against each other, sexually (no asexual reproduction)
    def cross_over(self, breeder_count):
        breeders = self.get_top_members(breeder_count)

        for breeder in breeders:
            for mate in breeders:
                # prevent asexual reproduction (this will cause result in clone wars)
                if mate is not breeder:
                    newborn = breeder.cross(mate)
                    newborn.mutate(0.075)
                    self.add_member(newborn, self.current_generation + 1)

    # TODO: track # of each type of action
    def draw(self):
        # Table 1: print leaderboard
        input_table = Texttable(max_width=115)
        input_table.set_deco(Texttable.HEADER | Texttable.BORDER)
        rows = []
        data_rows = []

        # header row
        rows.append(["ranking",
                     "skill game win rate (%)",
                     "score",
                     "skill game wins",
                     "coinflip game wins",
                     "game losses",
                     "total points",
                     "match losses",
                     "age"])

        # gather data on our population
        max_age = 0
        max_score = 0
        max_winrate = 0
        for item in self.member_genes.items():
            value = item[1]
            # collect values
            match_wins, match_losses = value['match_wins'], value['match_losses']
            coinflip_game_wins = value['coinflip_game_wins']

            # track maximum score
            score = self.ranking_func(value)
            if score > max_score:
                max_score = score


            game_wins           = value['game_wins']
            coinflip_game_wins  = value['coinflip_game_wins']
            game_losses         = value['game_losses']
            game_points         = value['game_points']
            match_losses        = value['match_losses']

            skill_game_wins = game_wins - coinflip_game_wins

            # calculate and track win rate
            try:
                winrate = (float(skill_game_wins) / float(skill_game_wins + game_losses))
            except ZeroDivisionError:
                winrate = 0.00

            if winrate > max_winrate:
                max_winrate = winrate

            # track maximum age
            age = self.current_generation - value['generation'] + 1
            if age > max_age:
                max_age = age

            # append values
            data_rows.append([winrate, score, skill_game_wins, coinflip_game_wins, game_losses, game_points, match_losses, age])

        # sort by winrate
        data_rows.sort(key=itemgetter(1), reverse=True)

        # collect the top min(10, self.population_size)
#        for i in range(min(10, len(data_rows))):
        for i in range(len(data_rows)):
            # what's our current ranking?
            one_row = [i + 1]
            # the other values defined in the header row
            for j in range(len(rows[0]) - 1):
                one_row.append(data_rows[i][j])
            rows.append(one_row)
#        input_table.add_rows(rows[:11])
        input_table.add_rows(rows)

        output_text = "\n" + "                     LEADERBOARD FOR GENERATION #{0}  (population: {1}".format(
            self.current_generation, len(self.member_genes))

        output_text += "\n" + input_table.draw()

        # log the best score to disk
        try:
            filename = self.local_storage + '.tally'
            with open(filename, 'a+') as the_file:
                best_score = rows[1][2]
                output = str(self.current_generation) + ',' + str(max_score) + ',' + str(max_winrate) + ',' + str(max_age) + "\n"
                the_file.write(output)
        except:
            pass

        return output_text

    def persist(self, action=None):
        assert action is not None, "must specify an action when calling persist()"
        # by default, do not persist
        if not self.local_storage:
            return False

        if action == 'store':
            try:
                pickle.dump(self, open(self.local_storage, 'w'))
                return True
            except:
                return False
        elif action == 'load':
            try:
                # we make a new copy of the object, then we copy its __dict__ into our own __dict__
                restored = pickle.load(open(self.local_storage, 'r'))
                for key in self.__dict__:
                    self.__dict__[key] = restored.__dict__[key]
                return True
            except:
                return False