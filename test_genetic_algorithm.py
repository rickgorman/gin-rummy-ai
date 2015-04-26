import unittest
from genetic_algorithm import *
import utility
import os

# static seed for repeatability
random.seed(0)


class TestGeneSet(unittest.TestCase):
    def setUp(self):
        pass

    def test___init__(self):
        # ensure we have 500 float weights between [0,1] in our geneset
        expected_genome_size = 500
        gs = GeneSet(expected_genome_size)
        self.assertEqual(expected_genome_size, len(gs.genes))
        for gene in gs.genes:
            self.assertGreaterEqual(gene, 0)
            self.assertLessEqual(gene, 1)

        # ensure we fail without being passed in an argument
        with self.assertRaises(AssertionError):
            GeneSet()

    def test___init__with_genes(self):
        # allow good genes in
        good_genes = [0.1, 0.2, 0.3, 0.4, 0.5]
        gs = GeneSet(good_genes)

        for i in range(len(good_genes)):
            self.assertEqual(good_genes[i], gs.genes[i])

        # prevent bad genes from being instantiated
        bad_genes  = [1, 2, 3]
        with self.assertRaises(AssertionError):
            GeneSet(bad_genes)

    def test_make_geneset(self):
        # ensure we return a GeneSet object
        gs = GeneSet(10)
        factory_gs = gs.make_geneset(10)
        self.assertIsInstance(factory_gs, GeneSet)

    def cross_with_partner_sizes(self, size1, size2):
        mom = GeneSet(size1)
        dad = GeneSet(size2)

        kid = mom.cross(dad)

        # test that at least some genes came from either parent (this test will fail often with small genomes)
        genes_from_small_partner = 0
        genes_from_big_partner = 0

        # test up to the length of the smallest partner's genome
        big_partner, small_partner = dad, mom
        if len(dad.genes) < len(mom.genes):
            big_partner, small_partner = mom, dad

        # test that each kid gene came from a parent
        for i in range(len(small_partner.genes)):
            if kid.genes[i] == small_partner.genes[i]:
                genes_from_small_partner += 1
            elif kid.genes[i] == big_partner.genes[i]:
                genes_from_big_partner += 1
            else:
                self.fail("gene did not come from either mom or dad")

        # if we don't get at least one gene from each partner, we blame the length of the small partner's genome.
        self.assertTrue(genes_from_small_partner >= 1 or len(small_partner.genes) <= 1)
        self.assertTrue(genes_from_big_partner   >= 1 or len(small_partner.genes) <= 1)

        # ensure the kid has the right number of genes (maximum size between mom/dad's genes)
        biggest_gene_set = max(len(mom.genes), len(dad.genes))
        self.assertEqual(len(kid.genes), biggest_gene_set)

    def test_cross(self):
        # test with genomes of various sizes
        self.cross_with_partner_sizes(100, 100)
        self.cross_with_partner_sizes(50, 100)
        self.cross_with_partner_sizes(100, 50)
        self.cross_with_partner_sizes(0, 100)
        self.cross_with_partner_sizes(100, 100)
        self.cross_with_partner_sizes(1, 1)
        self.cross_with_partner_sizes(1, 2)
        self.cross_with_partner_sizes(2, 1)

    def mutate_with_size_and_probability(self, size, probability):
        # with a big enough geneset, we should see some mutations (this will fail sometimes)
        gene_list = [0.0] * size
        gs = GeneSet(gene_list)
        gs.mutate(probability)

        # check for at least 1 element that is no longer 0
        zeroes_found = gs.genes.count(0)
        self.assertNotEqual(zeroes_found, len(gene_list))

    def test_mutate(self):
        self.mutate_with_size_and_probability(100000, 0.01)

        # ensure we do not mutate when passed a mutation rate of 0
        with self.assertRaises(AssertionError):
            self.mutate_with_size_and_probability(1000, 0.0)


class TestGinGeneSet(unittest.TestCase):
    def setUp(self):
        pass

    def test_make_geneset(self):
        # ensure we return a GinGeneSet object
        ggs = GinGeneSet(5)
        factory_gs = ggs.make_geneset(5)
        self.assertIsInstance(factory_gs, GinGeneSet)


class TestPopulation(unittest.TestCase):
    def setUp(self):
        self.gene_size = 100
        self.initial_population_size = 100
        self.p = Population(self.gene_size, self.initial_population_size)

    def test___init__(self):
        # test generation counter
        self.assertEqual(0, self.p.current_generation)

        # test structure
        first_member = self.p.member_genes.keys()[0]
        self.assertEqual(self.initial_population_size, len(self.p.member_genes.keys()))
        self.assertIsInstance(self.p.member_genes, dict)
        self.assertIsInstance(first_member, GeneSet)
        self.assertIsInstance(self.p.member_genes[first_member]['match_wins'], int)
        self.assertIsInstance(self.p.member_genes[first_member]['match_losses'], int)
        self.assertIsInstance(self.p.member_genes[first_member]['generation'], int)

    def test_draw(self):
        self.p.draw()

    def test_cull(self):
        # rig up 4 winners
        rig_count = 0
        for key in self.p.member_genes.keys():
            if rig_count > 4:
                break
            self.p.member_genes[key]['match_wins'] = 10
            self.p.member_genes[key]['generation'] = 0
            rig_count += 1

        # go to the future
        self.p.current_generation = 1

        # we expect to retain only 4 members from generation 0
        self.p.retain_best = 4
        self.p.cull()

        members_in_gen0 = 0
        for item in self.p.member_genes.items():
            if item[1]['generation'] == 0:
                members_in_gen0 += 1

        self.assertEqual(4, members_in_gen0)

    def test_persist(self):
        filename = '/tmp/test_persist.txt'
        self.p.local_storage = filename

        try:
            os.remove(filename)
        except OSError:
            pass

        self.p.current_generation = 25
        # store the population and reload it into a new variable
        self.p.persist(action='store')
        self.p.member_genes = {}
        self.p.persist(action='load')

        self.assertEqual(25, self.p.current_generation)
        self.assertEqual(self.initial_population_size, len(self.p.member_genes))
        self.assertEqual(self.gene_size, len(self.p.member_genes.keys()[0].genes))

    def test_ranking_func(self):
        gene_item = {'game_wins': 4, 'coinflip_game_wins': 4, 'game_losses': 0, 'generation': 0}
        self.assertEqual(0, self.p.ranking_func(gene_item))

        gene_item = {'game_wins': 4, 'coinflip_game_wins': 0, 'game_losses': 0, 'generation': 0}
        self.assertEqual(4, self.p.ranking_func(gene_item))

        gene_item = {'game_wins': 4, 'coinflip_game_wins': 2, 'game_losses': 0, 'generation': 0}
        self.assertEqual(2, self.p.ranking_func(gene_item))

        gene_item = {'game_wins': 4, 'coinflip_game_wins': 2, 'game_losses': 0, 'generation': 0}
        self.p.current_generation = 1
        self.assertEqual(1, self.p.ranking_func(gene_item))

    def test_get_top_members(self):
        # rig up 4 winners, all of whom won by coinflip
        rig_count = 0
        for key in self.p.member_genes.keys():
            if rig_count > 4:
                break
            self.p.member_genes[key]['match_wins'] = 1
            self.p.member_genes[key]['game_wins'] = 4
            self.p.member_genes[key]['coinflip_game_wins'] = 4
            self.p.member_genes[key]['generation'] = 0
            rig_count += 1

        # ensure they are returned
        top_keys = self.p.get_top_members(4)
        for key in top_keys:
            self.assertEqual(self.p.member_genes[key]['match_wins'], 1)

        # give another gene a lot of non-coinflip wins and ensure he is the top key
        key = self.p.member_genes.keys()[20]
        self.p.member_genes[key]['match_wins'] = 20
        self.p.member_genes[key]['game_wins'] = 20
        self.p.member_genes[key]['coinflip_game_wins'] = 0
        self.p.member_genes[key]['generation'] = 0

        top_keys = self.p.get_top_members(5)
        self.assertTrue(key in top_keys)

    def test_cross_over(self):
        breeder_count = 20
        self.p.cross_over(breeder_count)

        # we expect the population size to grow by 20^2 (self-mating NOT allowed)
        self.assertEqual(len(self.p.member_genes), breeder_count*(breeder_count - 1) + self.initial_population_size)

    def test_add_member(self):
        generation = 2
        self.p.member_genes = {}
        self.p.add_member(GeneSet(40), generation)

        self.assertEqual(1, len(self.p.member_genes))
        self.assertEqual(2, self.p.member_genes.items()[0][1]['generation'])

    def test_fitness_test(self):
        member_count = 4
        self.p.member_genes = {}
        for _ in range(member_count):
            self.p.add_member(GeneSet(4000), 0)

        # calculate number of matches as triangular series
        expected_games_played = (member_count * (member_count - 1)) / 2

        # run the fitness test and ensure one member has a win, and one has a loss, for each game played
        self.p.fitness_test()
        matches_won = 0
        matches_lost = 0

        for member in self.p.member_genes.items():
            matches_won  += member[1]['match_wins']
            matches_lost += member[1]['match_losses']

        self.assertEqual(expected_games_played, matches_won)
        self.assertEqual(expected_games_played, matches_lost)

    def test_generate_next_generation(self):
        self.gene_size = 4000
        self.initial_population_size = 6
        self.retain_best = 3
        self.p = Population(self.gene_size, self.initial_population_size, retain_best=self.retain_best)

        self.p.generate_next_generation()

        # advance the generation counter
        self.assertEqual(1, self.p.current_generation)

        # we expect to keep our population level small: initial + best
        self.assertGreaterEqual(self.initial_population_size + self.retain_best, len(self.p.member_genes))

        # run a few more generations and verify our population size has remained stable
        self.p.generate_next_generation()
        self.assertGreaterEqual(self.initial_population_size + self.retain_best, len(self.p.member_genes))
        self.p.generate_next_generation()
        self.assertGreaterEqual(self.initial_population_size + self.retain_best, len(self.p.member_genes))
        self.p.generate_next_generation()
        self.assertGreaterEqual(self.initial_population_size + self.retain_best, len(self.p.member_genes))

    def test_funking_around(self):
        self.population_size = 2
        self.gene_size = 4000
        self.max_generations = 1
        self.p = Population(self.gene_size, self.population_size, retain_best=4)

        for _ in range(self.max_generations):
            self.p.generate_next_generation()

        a = 1