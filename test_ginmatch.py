from ginmatch import *
from test_helpers import *


class TestGinMatch(Helper):

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

    def setUp(self):
        # set up the match
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()
        self.gm = GinMatch(self.p1, self.p2)

    def test__init__(self):
        # assign them to a match
        try:
            gm = GinMatch(self.p1, self.p2)
        except Exception:
            self.fail("Ginmatch() raised Exception unexpectedly!")

    def test_notify_of_knock(self):
        self.p1.knock()
        self.assertEqual(self.gm.player_who_knocked, self.p1)

    def test_notify_of_knock_gin(self):
        self.p1.knock_gin()
        self.assertEqual(self.gm.player_who_knocked_gin, self.p1)

    def test_run(self):
        # rig the horse with rockets
        self.gm.p1_score = 100

        # run the match and return the winner.
        winner = self.gm.run()

        # make sure the winner is our horse
        self.assertEqual(winner, self.p1)

    def test_play_game(self):
        pass

    def test_deal_cards(self):
        # assert player 1 receives 11 cards and player 2 receives 10 cards
        self.gm.deal_cards()

        self.assertEqual(11, self.p1.hand.size())
        self.assertEqual(10, self.p2.hand.size())

    def test_take_turns(self):
        # set up the match. we'll give p1 a gin-worthy hand and p2 a knock-worth hand (deadwood=1)
        self.p1 = GinPlayer(MockGinStrategy(['KNOCK', 10]))
        self.p2 = GinPlayer()
        self.gm = GinMatch(self.p1, self.p2)

        self.p1.hand = self.generate_ginhand_from_card_data(self.gin_worthy_hand_data)
        # give p1 an 11th card for discarding
        self.p1.hand.add(1, 'h')
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # after turn taking is done, we should reach the gameover state and have exactly one knocker
        self.gm.take_turns()
        self.assertTrue(self.gm.gameover)
        someone_knocked = self.gm.player_who_knocked != False
        someone_knocked_gin = self.gm.player_who_knocked_gin != False
        # use an xor to ensure we only had one knock
        self.assertTrue(someone_knocked ^ someone_knocked_gin)

    def test_end_with_knock_invalid(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was INVALID, ensure we penalize the player and that the game continues
        self.gm.end_with_knock(self.p1)
        self.assertTrue(self.gm.p1_knocked_improperly)
        self.assertFalse(self.gm.player_who_knocked)
        self.assertFalse(self.gm.gameover)

    def test_end_with_knock_valid(self):
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()
        self.gm = GinMatch(self.p1, self.p2)

        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was VALID, ensure we mark the game as over
        self.gm.end_with_knock(self.p2)
        self.assertFalse(self.gm.p2_knocked_improperly)
        self.assertTrue(self.gm.gameover)
        self.assertEqual(self.gm.player_who_knocked, self.p2)

    def test_end_with_knock_gin_invalid(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was INVALID, ensure we penalize the player and that the game continues
        self.gm.end_with_knock_gin(self.p1)
        self.assertTrue(self.gm.p1_knocked_improperly)
        self.assertFalse(self.gm.player_who_knocked)
        self.assertFalse(self.gm.gameover)

    def test_end_with_knock_gin_valid(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # gin-worthy hand with deadwood=0
        self.p2.hand = self.generate_ginhand_from_card_data(self.gin_worthy_hand_data)

        # if the knock was VALID, ensure we penalize the player and that the game continues
        self.gm.end_with_knock_gin(self.p2)
        self.assertFalse(self.gm.p2_knocked_improperly)
        self.assertEqual(self.gm.player_who_knocked_gin, self.p2)
        self.assertTrue(self.gm.gameover)

    def test_update_score_for_gin(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # gin-worthy hand with deadwood=0
        self.p2.hand = self.generate_ginhand_from_card_data(self.gin_worthy_hand_data)

        # knock
        self.p2.knock_gin()

        self.gm.update_score()
        self.assertEqual(self.gm.p1_score, 0)
        self.assertEqual(self.gm.p2_score, 55+25)

    def test_update_score_for_knock(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # knock
        self.p2.knock()

        self.gm.update_score()
        self.assertEqual(self.gm.p1_score, 0)
        self.assertEqual(self.gm.p2_score, 54)