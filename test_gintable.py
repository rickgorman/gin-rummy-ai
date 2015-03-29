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