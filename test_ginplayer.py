from ginplayer import *
from ginhand import *
from gintable import *
import unittest


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

    def test_sit_at_table(self):
        p = GinPlayer()
        t = GinTable()

        # sit down and ensure table is made of wood
        p._sit_at_table(t)
        self.assertIsInstance(p.table, GinTable, "Player not sitting at GinTable")

    def test__add_card(self):
        p = GinPlayer()

        # verify empty hand
        self.assertEqual(p.hand.size(), 0)

        # draw a card and verify length of hand is 1
        p._add_card(GinCard(9, 'c'))
        self.assertEqual(p.hand.size(), 1)

    def test_draw(self):
        p = GinPlayer()
        pass

    def test_pickup_discard(self):
        pass

    def test_discard_card(self):
        pass

    def test_knock(self):
        pass

