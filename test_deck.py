
from deck import *
import unittest
from operator import attrgetter


class TestCard(unittest.TestCase):

    def testNewCard(self):
        c = Card(1, 'c')

        self.assertEqual(c.rank, 1)
        self.assertEqual(c.suit, 'c')

    def testSanity(self):
        with self.assertRaises(AttributeError):
            Card(10, 'x')

        with self.assertRaises(AttributeError):
            Card(100, 'c')


class TestDeck(unittest.TestCase):
    def testNewDeck(self):
        d = Deck()
        self.assertEqual(len(d.cards), 52)

    def testShuffle(self):
        d = Deck()
        d.cards.sort(key=attrgetter('rank', 'suit'))
        before = d.examine()
        d.shuffle()
        self.assertNotEqual(before, d.examine())

    def testDealACard(self):
        d = Deck()
        topcard = d.cards[51]
        c = d.deal_a_card()
        self.assertEqual(51, len(d.cards))
        self.assertEqual(topcard, c)

    def testExamine(self):
        d = Deck()
        d.cards.sort(key=attrgetter('rank', 'suit'))
        top_card_rank = d.cards[0].rank
        examined_card_rank = d.examine()[0][0]
        self.assertEqual(top_card_rank, examined_card_rank)