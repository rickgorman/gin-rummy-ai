from ginmatch import *
import unittest
from test_helpers import *


class TestGinMatch(unittest.TestCase):

    awful_hand_data = [
        (1, 'd'),
        (2, 'c'),
        (3, 'd'),
        (4, 'c'),
        (5, 'c'),
        (6, 'd'),
        (7, 'c'),
        (8, 'd'),
        (9, 'c'),
        (10, 'd'),
    ]

    knock_worthy_hand_data = [
        (1, 'd'),
        (2, 'c'),
        (3, 'c'),
        (4, 'c'),
        (5, 'c'),
        (6, 'c'),
        (7, 'c'),
        (8, 'c'),
        (9, 'c'),
        (10, 'c'),
    ]

    gin_worthy_hand_data = [
        (1, 'c'),
        (2, 'c'),
        (3, 'c'),
        (4, 'c'),
        (5, 'c'),
        (6, 'c'),
        (7, 'c'),
        (8, 'c'),
        (9, 'c'),
        (10, 'c'),
    ]

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

        # after a game, scores should change (this breaks in case of a tie or deck running out)
        p1_score_before = 0
        p2_score_before = 0
        gm.play_game()
        self.assertNotEqual(p1_score_before + p2_score_before, gm.p1_score + gm.p2_score)

    def test_deal_cards(self):
        p1 = GinPlayer()
        p2 = GinPlayer()
        gm = GinMatch(p1, p2)

        # assert player 1 receives 11 cards and player 2 receives 10 cards
        gm.deal_cards()

        self.assertEqual(11, p1.hand.size())
        self.assertEqual(10, p2.hand.size())

    def test_end_with_knock_invalid(self):
        p1 = GinPlayer()
        p2 = GinPlayer()
        gm = GinMatch(p1, p2)

        # morbidly awful hand with deadwood = 55
        p1.hand = Helper.helper_generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        p2.hand = Helper.helper_generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was INVALID, ensure we penalize the player and that the game continues
        gm.end_with_knock(p1)
        self.assertTrue(gm.p1_knocked_improperly)
        self.assertFalse(gm.player_who_knocked)
        self.assertFalse(gm.gameover)

    def test_end_with_knock_valid(self):
        p1 = GinPlayer()
        p2 = GinPlayer()
        gm = GinMatch(p1, p2)

        # morbidly awful hand with deadwood = 55
        p1.hand = Helper.helper_generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        p2.hand = Helper.helper_generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was VALID, ensure we mark the game as over
        gm.end_with_knock(p2)
        self.assertFalse(gm.p2_knocked_improperly)
        self.assertTrue(gm.gameover)
        self.assertEqual(gm.player_who_knocked, p2)

    def test_end_with_knock_gin_invalid(self):
        p1 = GinPlayer()
        p2 = GinPlayer()
        gm = GinMatch(p1, p2)

        # morbidly awful hand with deadwood = 55
        p1.hand = Helper.helper_generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        p2.hand = Helper.helper_generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was INVALID, ensure we penalize the player and that the game continues
        gm.end_with_knock_gin(p1)
        self.assertTrue(gm.p1_knocked_improperly)
        self.assertFalse(gm.player_who_knocked)
        self.assertFalse(gm.gameover)

    def test_end_with_knock_gin_valid(self):
        p1 = GinPlayer()
        p2 = GinPlayer()
        gm = GinMatch(p1, p2)

        # morbidly awful hand with deadwood = 55
        p1.hand = Helper.helper_generate_ginhand_from_card_data(self.awful_hand_data)

        # gin-worthy hand with deadwood=0
        p2.hand = Helper.helper_generate_ginhand_from_card_data(self.gin_worthy_hand_data)

        # if the knock was VALID, ensure we penalize the player and that the game continues
        gm.end_with_knock_gin(p2)
        self.assertFalse(gm.p2_knocked_improperly)
        self.assertEqual(gm.player_knocked_gin, p2)
        self.assertTrue(gm.gameover)

    def test_update_score_for_gin(self):
        p1 = GinPlayer()
        p2 = GinPlayer()
        gm = GinMatch(p1, p2)

        # morbidly awful hand with deadwood = 55
        p1.hand = Helper.helper_generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=0
        p2.hand = Helper.helper_generate_ginhand_from_card_data(self.gin_worthy_hand_data)

        gm.update_score()
        self.assertEqual(gm.p1_score, 0)
        self.assertEqual(gm.p2_score, 55+25)
