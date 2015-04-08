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

        # we expect 52 entries for deck and 52 for discard pile
        self.assertEqual(104, len(data))

        # we should find a total of 52 0's, where 0 means there is no card there.
        zeroes = 0

        # record uniqueness of each card
        found = {}
        for i in range(104):
            if data[i] is 0:
                zeroes += 1
            else:
                self.assertTrue(data[i] not in found.keys())

            found[data[i]] = True

        # ensure we found 53 unique items
        self.assertEqual(53, len(found))
        # in all, 52 zeroes should be found between the deck and the discard pile.
        self.assertEqual(52, zeroes)

        ordered = sorted(found.keys())
        for i in range(0, len(found.keys())):
            self.assertEqual(i, ordered[i])

        # here we ensure the values are tightly contained within [0,52]
        self.assertTrue(min(found.keys()) >= 0)
        self.assertTrue(max(found.keys()) == 52)