from ginmatch import *
from test_helpers import *
from test_ginstrategy import MockGinStrategy


# noinspection PyProtectedMember
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
        self.c = GinCard(2, 'c')

        self.p2.strategy = MockGinStrategy(['DRAW'])

    def test__init__(self):
        # assign them to a match
        try:
            gm = GinMatch(self.p1, self.p2)
        except Exception:
            self.fail("Ginmatch() raised Exception unexpectedly!")

    def test_knock(self):
        self.gm.deal_cards()
        self.assertEqual(11, self.p1.hand.size())

        card_to_discard = self.p1.hand.cards[0]

        self.p1.knock(card_to_discard)
        self.assertEqual(10, self.p1.hand.size())
        self.assertFalse(self.p1.hand.contains_card(card_to_discard))

    # duplicate of test_knock
    def test_knock_gin(self):
        self.gm.deal_cards()
        self.assertEqual(11, self.p1.hand.size())

        card_to_discard = self.p1.hand.cards[0]

        self.p1.knock_gin(card_to_discard)
        self.assertEqual(10, self.p1.hand.size())
        self.assertFalse(self.p1.hand.contains_card(card_to_discard))

    def test_notify_of_knock(self):
        self.p1.knock(self.c)
        self.assertEqual(self.gm.player_who_knocked, self.p1)

    def test_notify_of_knock_gin(self):
        self.p1.knock_gin(self.c)
        self.assertEqual(self.gm.player_who_knocked_gin, self.p1)

    def test_organize_data(self):
        data = self.gm.organize_data()

        # we expect 5 values: player scores (p1,2p), player matches won (p1, p2) and knock point
        self.assertEqual(5, len(data.keys()))

        # knock point initializes as 10
        self.assertEqual(10, data[0])

        # scores and matches won initialize as 0
        self.assertEqual(0, data[1])
        self.assertEqual(0, data[2])
        self.assertEqual(0, data[3])
        self.assertEqual(0, data[4])

    def test_run(self):
        # rig the horse with rockets
        self.gm.p1_score = 100

        # run the match and return the winner.
        winner = self.gm.run()

        # make sure the winner is our horse
        self.assertEqual(winner, self.p1)

    def test_play_game(self):
        # all play_game does is reset some flags and call other methods. leaving it blank.
        pass

    def test_deal_cards(self):
        # assert player 1 receives 11 cards and player 2 receives 10 cards
        self.gm.deal_cards()

        self.assertEqual(11, self.p1.hand.size())
        self.assertEqual(10, self.p2.hand.size())

    def test_take_turns(self):
        # set up the match. we'll give p1 a gin-worthy hand and p2 a knock-worth hand (deadwood=1)
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()
        self.gm = GinMatch(self.p1, self.p2)
        self.p1.strategy = MockGinStrategy(['KNOCK', 10])

        self.p1.hand = self.generate_ginhand_from_card_data(self.gin_worthy_hand_data)
        # give p1 an 11th card for discarding
        self.p1.hand.add_card(GinCard(1, 'h'))
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # after turn taking is done, we should reach the gameover state and have exactly one knocker
        self.gm.take_turns()
        self.assertTrue(self.gm.gameover)
        someone_knocked = self.gm.player_who_knocked != False
        someone_knocked_gin = self.gm.player_who_knocked_gin != False
        # use an xor to ensure we o nly had one knock
        self.assertTrue(someone_knocked ^ someone_knocked_gin)

    def test_end_with_knock_invalid(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was INVALID, ensure we penalize the player by exposing his cards
        self.gm.process_knock(self.p1)
        self.assertTrue(self.gm.p1_knocked_improperly)
        self.assertFalse(self.gm.player_who_knocked)

    def test_end_with_knock_valid(self):
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()
        self.gm = GinMatch(self.p1, self.p2)

        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was VALID, ensure we mark the game as over
        self.gm.process_knock(self.p2)
        self.assertFalse(self.gm.p2_knocked_improperly)
        self.assertTrue(self.gm.gameover)
        self.assertEqual(self.gm.player_who_knocked, self.p2)

    def test_end_with_knock_gin_invalid(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # if the knock was INVALID, ensure we penalize the player by exposing the cards (also, gameover is not yet set)
        self.gm.process_knock_gin(self.p1)
        self.assertTrue(self.gm.p1_knocked_improperly)
        self.assertFalse(self.gm.player_who_knocked)

    def test_end_with_knock_gin_valid(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # gin-worthy hand with deadwood=0
        self.p2.hand = self.generate_ginhand_from_card_data(self.gin_worthy_hand_data)

        # if the knock was VALID, ensure we penalize the player and that the game continues
        self.gm.process_knock_gin(self.p2)
        self.assertFalse(self.gm.p2_knocked_improperly)
        self.assertEqual(self.gm.player_who_knocked_gin, self.p2)
        self.assertTrue(self.gm.gameover)

    def test_update_score_for_gin(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # gin-worthy hand with deadwood=0
        self.p2.hand = self.generate_ginhand_from_card_data(self.gin_worthy_hand_data)

        # add a card to discard
        dummy_card = GinCard(2, 'd')
        self.p2._add_card(dummy_card)

        # knock
        self.p2.knock_gin(dummy_card)

        self.gm.update_score()
        self.assertEqual(self.gm.p1_score, 0)
        self.assertEqual(self.gm.p2_score, 55+25)

    def test_update_score_for_knock(self):
        # morbidly awful hand with deadwood = 55
        self.p1.hand = self.generate_ginhand_from_card_data(self.awful_hand_data)

        # knock-worthy hand with deadwood=1
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)

        # add a card to discard
        dummy_card = GinCard(2, 'd')
        self.p2._add_card(dummy_card)

        # knock
        self.p2.knock(dummy_card)

        self.gm.update_score()
        self.assertEqual(self.gm.p1_score, 0)
        self.assertEqual(self.gm.p2_score, 54)

    def test_update_score_with_knock_undercut(self):
        # knock-worthy hand with deadwood=1
        self.p1.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)
        dummy_card = GinCard(2, 'd')
        self.p1._add_card(dummy_card)

        # for whatever reason, p2 decided to bm by not knocking gin
        self.p2.hand = self.generate_ginhand_from_card_data(self.gin_worthy_hand_data)

        # p1 knocks, believing he has the best hand
        self.p1.knock(dummy_card)

        self.gm.update_score()

        # verify that p2 gets the undercut bonus AND the deadwood points
        self.assertEqual(self.gm.p1_score, 0)
        self.assertEqual(self.gm.p2_score, 1+25)

    def test_offer_to_accept_improper_knock(self):
        # set up the improper knock conditions (here p1 knocks with deadwood=55, while p2 holds deadwood=1)
        self.test_end_with_knock_gin_invalid()

        # we force p2 to ACCEPT the knock
        self.p2.strategy.accept_improper_knock = self.return_true
        result = self.gm.offer_to_accept_improper_knock(self.p2)
        self.assertTrue(result)

        # ensure the game HAS been marked as over
        self.assertTrue(self.gm.gameover)

    def test_offer_to_accept_improper_knock_ineligible_accepter(self):
        # set up the improper knock conditions (here p1 knocks with deadwood=55, while p2 holds deadwood=37)
        self.test_end_with_knock_gin_invalid()
        self.p2.hand = self.generate_ginhand_from_card_data(self.card_data6_layoff)
        self.assertTrue(self.p2.hand.deadwood_count() > 10)
        self.gm.gameover = False

        # we instruct p2 to REJECT the knock
        self.p2.strategy.accept_improper_knock = self.return_false
        self.gm.offer_to_accept_improper_knock(self.p2)

        # ensure the game has NOT been marked as over
        self.assertFalse(self.gm.gameover)

    # note: while this looks similar to test_offer_to_accept_improper_knock_invalid, in this case we expect the
    # rejection to actually take place, whereas in the prior test, there is no option to reject due to p2's high
    # deadwood count.
    def test_offer_to_accept_improper_knock_decline(self):
        # set up the improper knock conditions (here p1 knocks with deadwood=55, while p2 holds deadwood=1)
        self.test_end_with_knock_gin_invalid()
        self.p2.hand = self.generate_ginhand_from_card_data(self.knock_worthy_hand_data)
        self.gm.gameover = False

        # we instruct p2 to REJECT the knock
        self.p2.accept_improper_knock = self.return_false
        result = self.gm.offer_to_accept_improper_knock(self.p2)
        self.assertFalse(result)

        # ensure the game has NOT been marked as over
        self.assertFalse(self.gm.gameover)

    def test_get_player_string(self):
        self.assertEqual(self.gm.get_player_string(self.p1), "player 1")
        self.assertEqual(self.gm.get_player_string(self.p2), "player 2")