from gintable import *
import unittest


class TestGinTable(unittest.TestCase):
    def test__init__(self):
        pass

    # seat two players normally, rejecting a third
    def test_seat_player_normal(self):
        t = GinTable()
        p1 = GinPlayer()
        p2 = GinPlayer()
        p3 = GinPlayer()

        # seat the first player
        t.seat_player(p1)
        self.assertEqual(t.player1, p1)

        # seat the second player
        t.seat_player(p2)
        self.assertEqual(t.player2, p2)

        # reject the third player
        self.assertRaises(TableSeatingError, t.seat_player, p3)

    # make sure we can't seat the same player twice
    def test_seat_player_twice(self):
        t = GinTable()
        p1 = GinPlayer()

        t.seat_player(p1)
        self.assertEqual(t.player1, p1)

        self.assertRaises(TableSeatingError, t.seat_player, p1)
