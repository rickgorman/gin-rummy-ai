from ginmatch import *
import unittest


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


# noinspection PyProtectedMember
class TestGinPlayer(unittest.TestCase):
    def test_new_ginplayer(self):
        s = GinStrategy()
        p = GinPlayer(s)

        # the guid shouldn't be a predictable number (this will fail 1 in 2**128 times)
        self.assertNotEqual(123456, p.id)

        # has a GinStrategy
        self.assertIsInstance(p.strategy, GinStrategy, "Does not contain a GinStrategy")

        # has a GinHand
        self.assertIsInstance(p.hand, GinHand, "Does not contain a GinHand")

        # allows other classes to observe potential knocks
        self.assertIsInstance(p._knock_listeners, list, "Does not implement observer on knocks")

        # allows other classes to observe potential gin calls
        self.assertIsInstance(p._knock_gin_listeners, list, "Does not implement observer on gins")

    def test__register_knock_listener(self):
        p = GinPlayer()
        l = MockListener()
        p.register_knock_listener(l)

        # verify the register happened
        self.assertEqual(1, len(p._knock_listeners))

        # verify we cant register a second time
        p.register_knock_listener(l)
        self.assertEqual(1, len(p._knock_listeners))

    # note that this also sufficiently tests knock()
    def test__notify_knock_listeners(self):
        p = GinPlayer()
        p.table = GinTable()
        l = MockListener()
        p.register_knock_listener(l)
        dummy_card = GinCard(2, 'd')
        p._add_card(dummy_card)

        # verify the knock callback occurs
        p.knock(dummy_card)
        self.assertEqual(True, l.did_it_knock)

        # verify we have the correct knocker
        self.assertEqual(p, l.knocker)

    def test__register_knock_gin_listener(self):
        p = GinPlayer()
        l = MockListener()
        p.register_knock_gin_listener(l)

        # verify the register happened
        self.assertEqual(1, len(p._knock_gin_listeners))

        # verity we cant register a second time
        p.register_knock_gin_listener(l)
        self.assertEqual(1, len(p._knock_gin_listeners))

    # note that this also sufficiently tests knock_gin()
    def test__notify_knock_gin_listener(self):
        p = GinPlayer()
        p.table = GinTable()
        l = MockListener()
        p.register_knock_gin_listener(l)
        dummy_card = GinCard(2, 'd')
        p._add_card(dummy_card)

        # verify the knock callback occurs
        p.knock_gin(dummy_card)
        self.assertEqual(True, l.did_it_knock_gin)

        # verify we have the correct knocker
        self.assertEqual(p, l.knocker)

    def test_sit_at_table(self):
        p = GinPlayer()
        t = GinTable()

        # sit down and ensure table is made of wood
        p.sit_at_table(t)
        self.assertIsInstance(p.table, GinTable, "Player not sitting at GinTable")

    def test__add_card(self):
        p = GinPlayer()

        # verify empty hand
        self.assertEqual(p.hand.size(), 0)

        # draw a card and verify length of hand is 1
        p._add_card(GinCard(9, 'c'))
        self.assertEqual(p.hand.size(), 1)

    def test_organize_data(self):
        p = GinPlayer()
        c1 = GinCard(2, 'c')
        c2 = GinCard(3, 'd')

        p._add_card(c1)
        p._add_card(c2)
        data = p.organize_data()

        self.assertIn(c1.ranking(), data.values())
        self.assertIn(c2.ranking(), data.values())

    def test_draw(self):
        t = GinTable()
        p = GinPlayer()
        p.sit_at_table(t)

        self.assertEqual(p.hand.size(), 0)
        p.draw()
        self.assertEqual(p.hand.size(), 1)
        p.draw()
        self.assertEqual(p.hand.size(), 2)
        for i in range(9):
            p.draw()
        self.assertEqual(p.hand.size(), 11)

        # ensure we cannot hold more than 11 cards
        self.assertRaises(DrawException, p.draw)

    def test_consult_strategy(self):
        strat = MockGinStrategy()
        p = GinPlayer(strat)

        # ensure the mock strategy give us exactly one action to perform
        self.assertEqual(False, p.action)
        p.consult_strategy()
        self.assertEqual('DISCARD', p.action[0])
        self.assertEqual(0, p.action[1])

    def test_execute_strategy_discard(self):
        strat = MockGinStrategy(['DISCARD', 0])
        p = GinPlayer(strat)
        p.table = GinTable()

        # monkey-load a card into the player's hand
        p.hand.add(4, 'c')

        # run the strategy, which should cause us to discard our first card
        p.consult_strategy()
        p.execute_strategy()
        self.assertEqual(0, p.hand.size())

    def test_execute_strategy_draw(self):
        strat = MockGinStrategy(['DRAW'])
        p = GinPlayer(strat)

        # monkey-patching in a table
        p.table = GinTable()

        # ensure the player picks up the card from the top of the deck.
        topcard = p.table.deck.cards[-1]
        self.assertEqual(0, p.hand.size())
        self.assertEqual(52, len(p.table.deck.cards))

        p.consult_strategy()
        p.execute_strategy()

        self.assertEqual(1, p.hand.size())
        self.assertTrue(p.hand.contains_card(topcard))
        self.assertEqual(51, len(p.table.deck.cards))

    def test_execute_strategy_pickup_discard(self):
        strat = MockGinStrategy(['PICKUP-DISCARD'])
        p = GinPlayer(strat)

        # monkey-patching in a table and a discard pile of depth 3
        p.table = GinTable()
        p.table.discard_pile.append(p.table.deck.cards.pop())
        p.table.discard_pile.append(p.table.deck.cards.pop())
        p.table.discard_pile.append(p.table.deck.cards.pop())

        # ensure the player picks up the card from the top of the discard pile
        topcard = p.table.discard_pile[-1]
        self.assertEqual(0, p.hand.size())
        self.assertEqual(49, len(p.table.deck.cards))

        p.consult_strategy()
        p.execute_strategy()

        self.assertEqual(1, p.hand.size())
        self.assertTrue(p.hand.contains_card(topcard))
        self.assertEqual(49, len(p.table.deck.cards))

    def test_execute_strategy_knock(self):
        strat = MockGinStrategy(['KNOCK', 0])
        p = GinPlayer(strat)
        p.table = GinTable()
        l = MockListener()
        p.register_knock_listener(l)

        # load up a fake hand. note these cards are chosen to be sorted into slots 0 and 1
        card_0 = Card(4, 'c')
        card_1 = Card(5, 'd')
        p.hand.add_card(card_0)
        p.hand.add_card(card_1)

        # run strategy
        p.consult_strategy()
        p.execute_strategy()

        # verify we discard card 0 into the discard pile AND the listener receives a knock
        self.assertEqual(1, p.hand.size())
        self.assertEqual(card_1, p.hand.cards[0])
        self.assertEqual(card_0, p.table.discard_pile[0])
        self.assertEqual(True, l.did_it_knock)

    def test_execute_strategy_knock_gin(self):
        strat = MockGinStrategy(['KNOCK-GIN', 0])
        p = GinPlayer(strat)
        p.table = GinTable()
        l = MockListener()
        p.register_knock_gin_listener(l)

        # load up a fake hand. note these cards are chosen to be sorted into slots 0 and 1
        card_0 = Card(4, 'c')
        card_1 = Card(5, 'd')
        p.hand.add_card(card_0)
        p.hand.add_card(card_1)

        # run strategy
        p.consult_strategy()
        p.execute_strategy()

        # verify we discard card 0 into the discard pile AND the listener receives a knock
        self.assertEqual(1, p.hand.size())
        self.assertEqual(card_1, p.hand.cards[0])
        self.assertEqual(1, len(p.table.discard_pile))
        self.assertEqual(card_0, p.table.discard_pile[0])
        self.assertEqual(True, l.did_it_knock_gin)

    def test_take_turn(self):
        s = MockGinStrategy(['DRAW'])
        p = GinPlayer(s)

        # verify we reach an error if we do not have enough cards in hand
        self.assertRaises(Exception, p.take_turn)

    def test_pickup_discard(self):
        t = GinTable()
        p = GinPlayer()
        p.sit_at_table(t)

        # monkey-patch a card into the discard pile
        t.discard_pile.append(GinCard(4, 'c'))

        # a player's hand should change after picking up a discard
        size_before = p.hand.size()
        p.pickup_discard()
        size_after = p.hand.size()
        self.assertNotEqual(size_before, size_after)
        self.assertTrue(p.hand.contains(4, 'c'))

    def test_discard_card(self):
        t = GinTable()
        p = GinPlayer()
        p.sit_at_table(t)

        # ensure our hand is empty
        self.assertEqual(0, p.hand.size())

        # draw a card and ensure we're holding it
        card = p.draw()
        self.assertEqual(1, p.hand.size())

        # discard it and ensure we have 0 cards in hand, and that it is on top of the discard pile
        p.discard_card(card)
        self.assertEqual(0, p.hand.size())
        self.assertEqual(card, t.discard_pile.pop())