from ginmatch import *
import unittest


class TestGinMatch(unittest.TestCase):
    def test__init__(self):
        # create some players
        p1 = GinPlayer()
        p2 = GinPlayer()

        # assign them to a match
        try:
            gm = GinMatch(p1, p2)
        except Exception:
            self.fail("Ginmatch() raised Exception unexpectedly!")

    def test_run(self):
        # set up the match
        p1 = GinPlayer()
        p2 = GinPlayer()
        gm = GinMatch(p1, p2)

        # rig the horse with rockets
        gm.p1_score = 100

        # run the match and return the winner.
        winner = gm.run()

        # make sure the winner is our horse
        self.assertEqual(winner, p1)

    def test_play_game(self):
        # set up the match
        p1 = GinPlayer()
        p2 = GinPlayer()
        gm = GinMatch(p1, p2)

        # both players should have at least 10 cards
        self.

        # after a game, scores should change (this breaks in case of a tie or deck running out)
        p1_score_before = 0
        p2_score_before = 0
        gm.play_game()
        self.assertNotEqual(p1_score_before + p2_score_before, gm.p1_score + gm.p2_score)

