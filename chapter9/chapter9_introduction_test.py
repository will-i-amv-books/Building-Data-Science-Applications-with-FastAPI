import unittest
from chapter9.chapter9_introduction import add


# With unittest


class TestChapter9Introduction(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)


# With pytest


def test_add(): # Function name should start with 'test'
    assert add(2, 3) == 5
