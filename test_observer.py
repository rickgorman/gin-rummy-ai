from observer import *
import unittest
from gindeck import GinCard
from ginplayer import GinPlayer


class MockObserver(Observer):
    def __init__(self, obj):
        self.times_called = 0
        super(MockObserver, self).__init__(obj)

    def observe(self, int_list):
        self.times_called += 1
        self.buffer = int_list


# noinspection PyProtectedMember
class TestObservable(unittest.TestCase):

    def setUp(self):
        self.c1 = GinCard(9, 'c')
        self.c2 = GinCard(5, 'd')
        self.p = GinPlayer()

    def test_register_observer(self):
        mobs = MockObserver(self.p)

        self.p.register_observer(mobs)

        # trigger the callback handling present in __setattr__
        self.p._add_card(self.c1)
        self.assertIn(mobs, self.p._observers)

        # ensure we cannot register more than once
        self.p.register_observer(mobs)
        self.assertEqual(1, len(self.p._observers))

    def test_notify_observers(self):
        # add a card AND THEN begin observing the player
        self.p._add_card(self.c1)
        self.mobs = MockObserver(self.p)

        # ensure we call the observe method
        self.p._add_card(self.c2)
        self.assertEqual(1, self.mobs.times_called)

        # and that we pass the int_list to the observer
        self.assertIn(self.c1.ranking(), self.mobs.buffer)
        self.assertIn(self.c2.ranking(), self.mobs.buffer)


# noinspection PyProtectedMember
class TestObserver(unittest.TestCase):
    def setUp(self):
        self.p = GinPlayer()
        self.obs = Observer(self.p)

        self.pobs = PlayerObserver(self.p)
        self.c1 = GinCard(9, 'c')
        self.c2 = GinCard(5, 'd')

    def test____init__(self):
        # ensure we have registered both of our callbacks with the observed player
        self.assertEqual(2, len(self.p._observers))

    def test_register(self):
        # remove callbacks which were added during obs.__init__()
        self.p._observers = []

        self.assertEqual(0, len(self.p._observers))

        self.obs.register(self.p)
        self.assertEqual(1, len(self.p._observers))

    def test_get_value_by_index(self):
        # draw a few cards and ensure we can get the ith card's ranking
        cards = [GinCard(2, 'd'), GinCard(3, 'h'), GinCard(5, 'c')]
        for i in range(3):
            self.p._add_card(cards[i])
            self.assertEqual(self.pobs.get_value_by_index(i), self.p.hand.cards[i].ranking())

    def test_observe(self):
        # we expect the PlayerObserver's buffer to hold an array of ints representing the player's cards
        self.p._add_card(self.c1)
        self.assertIn(self.c1.ranking(), self.pobs.buffer)

        self.p._add_card(self.c2)
        self.assertIn(self.c1.ranking(), self.pobs.buffer)
        self.assertIn(self.c2.ranking(), self.pobs.buffer)


class TestPlayerObserver(unittest.TestCase):
    pass
