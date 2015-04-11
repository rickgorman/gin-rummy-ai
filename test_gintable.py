from gintable import *
import unittest


class TestGinTable(unittest.TestCase):
    def test__init__(self):
        pass

    def setUp(self):
        self.t = GinTable()
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()
        self.p3 = GinPlayer()

    # seat two players normally, rejecting a third
    def test_seat_player_normal(self):

        # seat the first player
        self.t.seat_player(self.p1)
        self.assertEqual(self.t.player1, self.p1)
        self.assertEqual(self.p1.table, self.t)

        # seat the second player
        self.t.seat_player(self.p2)
        self.assertEqual(self.t.player2, self.p2)
        self.assertEqual(self.p2.table, self.t)

        # reject the third player
        self.assertRaises(TableSeatingError, self.t.seat_player, self.p3)

    # make sure we can't seat the same player twice
    def test_seat_player_twice(self):
        self.t.seat_player(self.p1)
        self.assertEqual(self.t.player1, self.p1)

        self.assertRaises(TableSeatingError, self.t.seat_player, self.p1)

    # ensure we return the current deck, as well as the discard pile
    def test_organize_data(self):
        # we move a few cards into the discard pile
        self.t.discard_pile.append(self.t.deck.cards.pop())
        self.t.discard_pile.append(self.t.deck.cards.pop())
        self.t.discard_pile.append(self.t.deck.cards.pop())

        data = self.t.organize_data()

        # we expect one entry representing our deck size and 32 for discard pile
        self.assertEqual(33, len(data))

        # record uniqueness of each card
        found = {}
        zeroes = 0
        for i in range(1,33):
            if data[i] is 0:
                zeroes += 1
            else:
                self.assertTrue(data[i] not in found.keys())
            found[data[i]] = True

        # here we ensure the values are tightly contained within [0,52]
        self.assertTrue(min(found.keys()) >= 0)
        self.assertTrue(max(found.keys()) <= 52)

    def test_deal_a_card(self):
        card = self.t.deal_a_card()
        self.assertIsInstance(card, GinCard)
        self.assertTrue(card.ranking() not in [x.ranking() for x in self.t.deck.cards])

    def test_add_card_to_discard_pile(self):
        card = self.t.deal_a_card()
        self.t.add_card_to_discard_pile(card)
        self.assertTrue(card.ranking() in [x.ranking() for x in self.t.discard_pile])

    def test_pickup_from_discard_pile(self):
        # first, from empty discard pile
        with self.assertRaises(InvalidPlayError):
            card = self.t.pickup_from_discard_pile()

        # now, safely
        self.t.add_card_to_discard_pile(self.t.deal_a_card())
        card = self.t.pickup_from_discard_pile()

        self.assertIsInstance(card, GinCard)
        self.assertTrue(card.ranking() not in [x.ranking() for x in self.t.discard_pile])

    def test_refresh_deck(self):
        first_deck = self.t.deck.cards.__repr__()
        self.t.discard_pile.append(self.t.deck.deal_a_card())

        # refresh and make sure the deck isn't the same (this fails every so often)
        self.t.refresh_deck()
        self.assertEqual(52, len(self.t.deck.cards))
        second_deck = self.t.deck.cards.__repr__()
        self.assertEqual(0, len(self.t.discard_pile))

        self.assertNotEqual(first_deck, second_deck)