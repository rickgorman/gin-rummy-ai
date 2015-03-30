from observer import *
import unittest
from gindeck import GinCard
from ginplayer import GinPlayer


class MockObserver(object):
    def __init__(self):
        self.times_called = 0

    def observe(self, int_list):
        self.times_called += 1
        return int_list

    def register(self, obj):
        obj.add_callback(self.observe)


class TestObservable(unittest.TestCase):

    def setUp(self):
        self.c = GinCard(9, 'c')
        self.w = Observable(self.c)

    def test___setattr__(self):
        self.w.rank = 5
        self.assertEqual(5, self.c.rank)

    def test___getattr__(self):
        # test a property
        self.assertEqual(9, self.w.rank)

        # test a method
        self.assertEqual('9c', self.w.to_s())

    def test_register_observer(self):
        mobs = MockObserver()

        self.w.register_observer(mobs)

        # trigger the callback handling present in __setattr__
        self.w.rank = 4
        self.assertEqual(1, mobs.times_called)

        # ensure we cannot register more than once
        self.w.register_observer(mobs)
        self.assertEqual(1, len(self.w._callbacks))


# noinspection PyProtectedMember
class TestObserver(unittest.TestCase):
    def setUp(self):
        self.player = GinPlayer()
        self.p = Observable(self.player)
        self.obs = Observer(self.p)

    def test____init__(self):
        # ensure we have registered our callback with the observed player
        self.assertEqual(1, len(self.p._callbacks))

    def test_register(self):
        # remove callback which was added during obs.__init__()
        self.p._callbacks.pop()
        self.assertEqual(0, len(self.p._callbacks))

        self.obs.register(self.p)
        self.assertEqual(1, len(self.p._callbacks))