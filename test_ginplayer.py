from ginplayer import *
import unittest


class TestGinPlayer(unittest.TestCase):
    def test_new_ginplayer(self):
        p = GinPlayer()

        # the guid shouldn't be a predictable number (this will fail 1 in 2**128 times)
        self.assertNotEqual(0, p.id)
