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
        self.p = GinPlayer()
        self.p2 = GinPlayer()

        self.l = MockListener()
        self.t = GinTable()
        self.p.sit_at_table(self.t)

        self.gm = MockGinMatch()

    def test_new_ginplayer(self):
        # the guid shouldn't be a predictable number (this will fail 1 in 2**128 times)
        self.assertNotEqual(123456, self.p.id)

        # has a GinStrategy
        #        self.assertIsInstance(self.p.strategy, GinStrategy, "Does not contain a GinStrategy")

        # has a GinHand
        self.assertIsInstance(self.p.hand, GinHand, "Does not contain a GinHand")

        # allows other classes to observe potential knocks
        self.assertIsInstance(self.p._knock_listeners, list, "Does not implement observer on knocks")

        # allows other classes to observe potential gin calls
        self.assertIsInstance(self.p._knock_gin_listeners, list, "Does not implement observer on gins")

    def test__register_knock_listener(self):
        self.p = GinPlayer()
        self.p.register_knock_listener(self.l)

        # verify the register happened
        self.assertEqual(1, len(self.p._knock_listeners))

        # verify we cant register a second time
        self.p.register_knock_listener(self.l)
        self.assertEqual(1, len(self.p._knock_listeners))

    # note that this also sufficiently tests knock()
    def test__notify_knock_listeners(self):
        self.p.register_knock_listener(self.l)
        dummy_card = GinCard(2, 'd')
        self.p._add_card(dummy_card)

        # verify the knock callback occurs
        self.p.knock(dummy_card)
        self.assertEqual(True, self.l.did_it_knock)

        # verify we have the correct knocker
        self.assertEqual(self.p, self.l.knocker)

    def test__register_knock_gin_listener(self):
        self.p.register_knock_gin_listener(self.l)

        # verify the register happened
        self.assertEqual(1, len(self.p._knock_gin_listeners))

        # verity we cannot register a second time
        self.p.register_knock_gin_listener(self.l)
        self.assertEqual(1, len(self.p._knock_gin_listeners))

    # note that this also sufficiently tests knock_gin()
    def test__notify_knock_gin_listener(self):
        self.p.register_knock_gin_listener(self.l)

        dummy_card = GinCard(2, 'd')
        self.p._add_card(dummy_card)

        # verify the knock callback occurs
        self.p.knock_gin(dummy_card)
        self.assertEqual(True, self.l.did_it_knock_gin)

        # verify we have the correct knocker
        self.assertEqual(self.p, self.l.knocker)

    def test_sit_at_table(self):
        # empty the table as set up in setUp:
        self.p.table = False
        self.t.player1 = False
        self.t.player2 = False

        # sit down and ensure table is made of wood
        self.p.sit_at_table(self.t)
        self.assertIsInstance(self.p.table, GinTable, "Player not sitting at GinTable")

    def test__add_card(self):
        # verify empty hand
        self.assertEqual(self.p.hand.size(), 0)

        # draw a card and verify length of hand is 1
        self.p._add_card(GinCard(9, 'c'))
        self.assertEqual(self.p.hand.size(), 1)

    def test_organize_data(self):
        c1 = GinCard(2, 'c')
        c2 = GinCard(3, 'd')

        self.p._add_card(c1)
        self.p._add_card(c2)
        data = self.p.organize_data()

        self.assertIn(c1.ranking(), data.values())
        self.assertIn(c2.ranking(), data.values())

    def test_draw(self):
        self.assertEqual(self.p.hand.size(), 0)
        self.p.draw()
        self.assertEqual(self.p.hand.size(), 1)
        self.p.draw()
        self.assertEqual(self.p.hand.size(), 2)
        for i in range(9):
            self.p.draw()
        self.assertEqual(self.p.hand.size(), 11)

        # ensure we cannot hold more than 11 cards
        self.assertRaises(DrawException, self.p.draw)

    def test_consult_strategy(self):
        strat = MockGinStrategy({'end': ['DISCARD', 0]})
        self.p.strategy = strat

        # ensure the mock strategy gives us exactly one action to perform
        self.assertEqual(False, self.p.action)
        self.p.consult_strategy(phase='end')
        self.assertEqual('DISCARD', self.p.action[0])
        self.assertEqual(0, self.p.action[1])

    def test_execute_strategy_discard(self):
        strat = MockGinStrategy({'end': ['DISCARD', 0]})
        self.p.strategy = strat

        # monkey-load a card into the player's hand
        self.p.hand.add_card(GinCard(4, 'c'))

        # run the strategy, which should cause us to discard our first card
        self.p.consult_strategy(phase='end')
        self.p.execute_strategy()
        self.assertEqual(0, self.p.hand.size())

    def test_execute_strategy_draw(self):
        strat = MockGinStrategy({'start': ['DRAW']})
        self.p.strategy = strat

        # monkey-patching in a table
        #        self.p.table = GinTable()

        # ensure the player picks up the card from the top of the deck.
        topcard = self.p.table.deck.cards[-1]
        self.assertEqual(0, self.p.hand.size())
        self.assertEqual(52, len(self.p.table.deck.cards))

        self.p.consult_strategy(phase='start')
        self.p.execute_strategy()

        self.assertEqual(1, self.p.hand.size())
        self.assertTrue(self.p.hand.contains_card(topcard))
        self.assertEqual(51, len(self.p.table.deck.cards))

    def test_execute_strategy_pickup_discard(self):
        strat = MockGinStrategy({'start': ['PICKUP-FROM-DISCARD']})
        self.p.strategy = strat

        # monkey-patching in a table and a discard pile of depth 3
        #        p.table = GinTable()
        self.p.table.discard_pile.append(self.p.table.deck.cards.pop())
        self.p.table.discard_pile.append(self.p.table.deck.cards.pop())
        self.p.table.discard_pile.append(self.p.table.deck.cards.pop())

        # ensure the player picks up the card from the top of the discard pile
        topcard = self.p.table.discard_pile[-1]
        self.assertEqual(0, self.p.hand.size())
        self.assertEqual(49, len(self.p.table.deck.cards))

        self.p.consult_strategy(phase='start')
        self.p.execute_strategy()

        self.assertEqual(1, self.p.hand.size())
        self.assertTrue(self.p.hand.contains_card(topcard))
        self.assertEqual(49, len(self.p.table.deck.cards))

    def test_execute_strategy_knock(self):
        self.p.register_knock_listener(self.l)

        strat = MockGinStrategy({'end': ['KNOCK', 0]})
        self.p.strategy = strat

        # load up a fake hand. note these cards are chosen to be sorted into slots 0 and 1
        card_0 = Card(4, 'c')
        card_1 = Card(5, 'd')
        self.p.hand.add_card(card_0)
        self.p.hand.add_card(card_1)

        # run strategy
        self.p.consult_strategy(phase='end')
        self.p.execute_strategy()

        # verify we discard card 0 into the discard pile AND the listener receives a knock
        self.assertEqual(1, self.p.hand.size())
        self.assertEqual(card_1, self.p.hand.cards[0])
        self.assertEqual(card_0, self.p.table.discard_pile[0])
        self.assertEqual(True, self.l.did_it_knock)

    def test_execute_strategy_knock_gin(self):
        self.p.register_knock_gin_listener(self.l)

        strat = MockGinStrategy({'end': ['KNOCK-GIN', 0]})
        self.p.strategy = strat

        # load up a fake hand. note these cards are chosen to be sorted into slots 0 and 1
        card_0 = Card(4, 'c')
        card_1 = Card(5, 'd')
        self.p.hand.add_card(card_0)
        self.p.hand.add_card(card_1)

        # run strategy
        self.p.consult_strategy(phase='end')
        self.p.execute_strategy()

        # verify we discard card 0 into the discard pile AND the listener receives a knock
        self.assertEqual(1, self.p.hand.size())
        self.assertEqual(card_1, self.p.hand.cards[0])
        self.assertEqual(1, len(self.p.table.discard_pile))
        self.assertEqual(card_0, self.p.table.discard_pile[0])
        self.assertEqual(True, self.l.did_it_knock_gin)

    def test_take_turn(self):
        strat = MockGinStrategy({'end': ['DRAW']})
        self.p.strategy = strat

        self.p.hand = GinHand()

        # verify we reach an error if we do not have enough cards in hand
        self.assertRaises(AssertionError, self.p.take_turn)

    def test_pickup_discard(self):
        # monkey-patch a card into the discard pile
        self.t.discard_pile.append(GinCard(4, 'c'))

        # a player's hand should change after picking up a discard
        size_before = self.p.hand.size()
        self.p.pickup_discard()
        size_after = self.p.hand.size()
        self.assertNotEqual(size_before, size_after)
        self.assertTrue(self.p.hand.contains(4, 'c'))

    def test_discard_card(self):
        # ensure our hand is empty
        self.assertEqual(0, self.p.hand.size())

        # draw a card and ensure we're holding it
        card = self.p.draw()
        self.assertEqual(1, self.p.hand.size())

        # discard it and ensure we have 0 cards in hand, and that it is on top of the discard pile
        self.p.discard_card(card)
        self.assertEqual(0, self.p.hand.size())
        self.assertEqual(card, self.t.discard_pile.pop())

    def test_accept_improper_knock(self):
        # verify that we return whatever the mock strategy says to return
        self.p.strategy = MockGinStrategy({'start': ['WHATEVER']})
        self.assertTrue(self.p.accept_improper_knock())

    def test_empty_hand(self):
        self.p.hand = self.generate_ginhand_from_card_data(self.card_data1)
        self.p.empty_hand()
        self.assertEqual(0, len(self.p.hand.cards))