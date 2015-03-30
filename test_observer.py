from observer import *
import unittest
from gindeck import GinCard


class TestWrapper(unittest.TestCase):
    def setUp(self):
        self.c = GinCard(9, 'c')
        self.w = Wrapper(self.c)

    def test___setattr__(self):
        self.w.rank = 5
        self.assertEqual(5, self.c.rank)

    def test___getattr__(self):
        # test a property
        self.assertEqual(9, self.w.rank)

        # test a method
        self.assertEqual('9c', self.w.to_s())

    def test_add_callback(self):
        called = []

        def callback(obj):
            called.append('callback')

        self.w.add_callback(callback)

        # trigger the callback handling present in __setattr__
        self.w.rank = 4

        self.assertIn('callback', called)