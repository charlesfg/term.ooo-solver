import unittest
from unittest import TestCase

from guest5word import Game


class TestGame(TestCase):

    def test_play_1(self):
        g = Game("porra", 5)
        self.assertEqual("x?xx?", g.play("saber"))
        self.assertEqual("x?x!!", g.play("arara"))
        self.assertEqual("x?xxx", g.play("bates"))
        self.assertEqual("x?x?x", g.play("cagou"))
        self.assertEqual("x?xxx", g.play("canas"))
        self.assertEqual("x?xxx", g.play("canas"))
        self.assertRaises(Exception, g.play("canas"))



if __name__ == '__main__':
    unittest.main()
