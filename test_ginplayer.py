from ginmatch import *
import unittest
from test_ginstrategy import MockGinStrategy
from test_helpers import *


class MockListener:
    def __init__(self):
        self.did_it_knock = False
        self.did_it_knock_gin = False
        self.knocker = None

    def notify_of_knock(self, knocker):
        self.did_it_knock = True
        self.knocker = knocker

    def notify_of_knock_gin(self, knocker):
        self.did_it_knock_gin = True
        self.knocker = knocker


class MockGinMatch(object):
    def __init__(self):
        pass


# noinspection PyProtectedMember
class TestGinPlayer(Helper):
    def setUp(self):
        self.p1 = GinPlayer()
        self.p2 = GinPlayer()

        self.l = MockListener()
        self.t = GinTable()
        self.p1.sit_at_table(self.t)

        self.gm = MockGinMatch()

    def test_new_ginplayer(self):
        # the guid shouldn't be a predictable number (this will fail 1 in 2**128 times)
        self.assertNotEqual(123456, self.p1.id)

        # has a GinStrategy
        #        self.assertIsInstance(self.p.strategy, GinStrategy, "Does not contain a GinStrategy")

        # has a GinHand
        self.assertIsInstance(self.p1.hand, GinHand, "Does not contain a GinHand")

        # allows other classes to observe potential knocks
        self.assertIsInstance(self.p1._knock_listeners, list, "Does not implement observer on knocks")

        # allows other classes to observe potential gin calls
        self.assertIsInstance(self.p1._knock_gin_listeners, list, "Does not implement observer on gins")

    def test__register_knock_listener(self):
        self.p1 = GinPlayer()
        self.p1.register_knock_listener(self.l)

        # verify the register happened
        self.assertEqual(1, len(self.p1._knock_listeners))

        # verify we cant register a second time
        self.p1.register_knock_listener(self.l)
        self.assertEqual(1, len(self.p1._knock_listeners))

    # note that this also sufficiently tests knock()
    def test__notify_knock_listeners(self):
        self.p1.register_knock_listener(self.l)
        dummy_card = GinCard(2, 'd')
        self.p1._add_card(dummy_card)

        # verify the knock callback occurs
        self.p1.knock(dummy_card)
        self.assertEqual(True, self.l.did_it_knock)

        # verify we have the correct knocker
        self.assertEqual(self.p1, self.l.knocker)

    def test__register_knock_gin_listener(self):
        self.p1.register_knock_gin_listener(self.l)

        # verify the register happened
        self.assertEqual(1, len(self.p1._knock_gin_listeners))

        # verity we cannot register a second time
        self.p1.register_knock_gin_listener(self.l)
        self.assertEqual(1, len(self.p1._knock_gin_listeners))

    # note that this also sufficiently tests knock_gin()
    def test__notify_knock_gin_listener(self):
        self.p1.register_knock_gin_listener(self.l)

        dummy_card = GinCard(2, 'd')
        self.p1._add_card(dummy_card)

        # verify the knock callback occurs
        self.p1.knock_gin(dummy_card)
        self.assertEqual(True, self.l.did_it_knock_gin)

        # verify we have the correct knocker
        self.assertEqual(self.p1, self.l.knocker)

    def test_sit_at_table(self):
        # empty the table as set up in setUp:
        self.p1.table = False
        self.t.player1 = False
        self.t.player2 = False

        # sit down and ensure table is made of wood
        self.p1.sit_at_table(self.t)
        self.assertIsInstance(self.p1.table, GinTable, "Player not sitting at GinTable")

    def test__add_card(self):
        # verify empty hand
        self.assertEqual(self.p1.hand.size(), 0)

        # draw a card and verify length of hand is 1
        self.p1._add_card(GinCard(9, 'c'))
        self.assertEqual(self.p1.hand.size(), 1)

    def test_organize_data(self):
        c1 = GinCard(2, 'c')
        c2 = GinCard(3, 'd')

        self.p1._add_card(c1)
        self.p1._add_card(c2)
        data = self.p1.organize_data()

        self.assertIn(c1.ranking(), data.values())
        self.assertIn(c2.ranking(), data.values())

    def test_draw(self):
        self.assertEqual(self.p1.hand.size(), 0)
        self.p1.draw()
        self.assertEqual(self.p1.hand.size(), 1)
        self.p1.draw()
        self.assertEqual(self.p1.hand.size(), 2)
        for i in range(9):
            self.p1.draw()
        self.assertEqual(self.p1.hand.size(), 11)

        # ensure we cannot hold more than 11 cards
        self.assertRaises(DrawException, self.p1.draw)

    def test_consult_strategy(self):
        strat = MockGinStrategy({'end': ['DISCARD', 0]})
        self.p1.strategy = strat

        # ensure the mock strategy gives us exactly one action to perform
        self.assertEqual(False, self.p1.action)
        self.p1.consult_strategy(phase='end')
        self.assertEqual('DISCARD', self.p1.action[0])
        self.assertEqual(0, self.p1.action[1])

    def test_execute_strategy_discard(self):
        strat = MockGinStrategy({'end': ['DISCARD', 0]})
        self.p1.strategy = strat

        # monkey-load a card into the player's hand
        self.p1.hand.add_card(GinCard(4, 'c'))

        # run the strategy, which should cause us to discard our first card
        self.p1.consult_strategy(phase='end')
        self.p1.execute_strategy()
        self.assertEqual(0, self.p1.hand.size())

    def test_execute_strategy_draw(self):
        strat = MockGinStrategy({'start': ['DRAW']})
        self.p1.strategy = strat

        # monkey-patching in a table
        #        self.p.table = GinTable()

        # ensure the player picks up the card from the top of the deck.
        topcard = self.p1.table.deck.cards[-1]
        self.assertEqual(0, self.p1.hand.size())
        self.assertEqual(52, len(self.p1.table.deck.cards))

        self.p1.consult_strategy(phase='start')
        self.p1.execute_strategy()

        self.assertEqual(1, self.p1.hand.size())
        self.assertTrue(self.p1.hand.contains_card(topcard))
        self.assertEqual(51, len(self.p1.table.deck.cards))

    def test_execute_strategy_pickup_discard(self):
        strat = MockGinStrategy({'start': ['PICKUP-FROM-DISCARD']})
        self.p1.strategy = strat

        # monkey-patching in a table and a discard pile of depth 3
        #        p.table = GinTable()
        self.p1.table.discard_pile.append(self.p1.table.deck.cards.pop())
        self.p1.table.discard_pile.append(self.p1.table.deck.cards.pop())
        self.p1.table.discard_pile.append(self.p1.table.deck.cards.pop())

        # ensure the player picks up the card from the top of the discard pile
        topcard = self.p1.table.discard_pile[-1]
        self.assertEqual(0, self.p1.hand.size())
        self.assertEqual(49, len(self.p1.table.deck.cards))

        self.p1.consult_strategy(phase='start')
        self.p1.execute_strategy()

        self.assertEqual(1, self.p1.hand.size())
        self.assertTrue(self.p1.hand.contains_card(topcard))
        self.assertEqual(49, len(self.p1.table.deck.cards))

    def test_execute_strategy_knock(self):
        self.p1.register_knock_listener(self.l)

        strat = MockGinStrategy({'end': ['KNOCK', 0]})
        self.p1.strategy = strat

        # load up a fake hand. note these cards are chosen to be sorted into slots 0 and 1
        card_0 = Card(4, 'c')
        card_1 = Card(5, 'd')
        self.p1.hand.add_card(card_0)
        self.p1.hand.add_card(card_1)

        # run strategy
        self.p1.consult_strategy(phase='end')
        self.p1.execute_strategy()

        # verify we discard card 0 into the discard pile AND the listener receives a knock
        self.assertEqual(1, self.p1.hand.size())
        self.assertEqual(card_1, self.p1.hand.cards[0])
        self.assertEqual(card_0, self.p1.table.discard_pile[0])
        self.assertEqual(True, self.l.did_it_knock)

    def test_execute_strategy_knock_gin(self):
        self.p1.register_knock_gin_listener(self.l)

        strat = MockGinStrategy({'end': ['KNOCK-GIN', 0]})
        self.p1.strategy = strat

        # load up a fake hand. note these cards are chosen to be sorted into slots 0 and 1
        card_0 = Card(4, 'c')
        card_1 = Card(5, 'd')
        self.p1.hand.add_card(card_0)
        self.p1.hand.add_card(card_1)

        # run strategy
        self.p1.consult_strategy(phase='end')
        self.p1.execute_strategy()

        # verify we discard card 0 into the discard pile AND the listener receives a knock
        self.assertEqual(1, self.p1.hand.size())
        self.assertEqual(card_1, self.p1.hand.cards[0])
        self.assertEqual(1, len(self.p1.table.discard_pile))
        self.assertEqual(card_0, self.p1.table.discard_pile[0])
        self.assertEqual(True, self.l.did_it_knock_gin)

    def test_take_turn(self):
        strat = MockGinStrategy({'end': ['DRAW']})
        self.p1.strategy = strat

        self.p1.hand = GinHand()

        # verify we reach an error if we do not have enough cards in hand
        self.assertRaises(AssertionError, self.p1.take_turn)

    def test_pickup_discard(self):
        # monkey-patch a card into the discard pile
        self.t.discard_pile.append(GinCard(4, 'c'))

        # a player's hand should change after picking up a discard
        size_before = self.p1.hand.size()
        self.p1.pickup_discard()
        size_after = self.p1.hand.size()
        self.assertNotEqual(size_before, size_after)
        self.assertTrue(self.p1.hand.contains(4, 'c'))

    def test_discard_card(self):
        # ensure our hand is empty
        self.assertEqual(0, self.p1.hand.size())

        # draw a card and ensure we're holding it
        card = self.p1.draw()
        self.assertEqual(1, self.p1.hand.size())

        # discard it and ensure we have 0 cards in hand, and that it is on top of the discard pile
        self.p1.discard_card(card)
        self.assertEqual(0, self.p1.hand.size())
        self.assertEqual(card, self.t.discard_pile.pop())

    def test_accept_improper_knock(self):
        # verify that we return whatever the mock strategy says to return
        self.p1.strategy = MockGinStrategy({'start': ['WHATEVER']})
        self.assertTrue(self.p1.accept_improper_knock())

    def test_empty_hand(self):
        self.p1.hand = self.generate_ginhand_from_card_data(self.card_data1)
        self.p1.empty_hand()
        self.assertEqual(0, len(self.p1.hand.cards))