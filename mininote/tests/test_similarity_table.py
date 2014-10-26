from unittest import TestCase
from mininote.diff_notes import SimilarityTable


def diff(item1, item2):
    return -abs(item1 - item2)

class TestSimilarityTable(TestCase):

    def test_get_similarity(self):
        table = SimilarityTable([0, 1], [0, 2], diff)

        self.assertEqual(0, table.compare(0, 0))
        self.assertEqual(-1, table.compare(1, 1))

        self.assertEqual(-1, table.compare(1, 0))
        self.assertEqual(-2, table.compare(0, 1))

    def test_get_inexact_matches(self):
        table = SimilarityTable([0, 1], [0.1, 1.1], diff)

        self.assertEqual([0, 1], list(table.matches(0)))
        self.assertEqual([1, 0], list(table.matches(1)))

    def test_get_exact_matches(self):
        table = SimilarityTable([0, 1], [0, 1], diff)

        self.assertEqual([0, 1], list(table.matches(0)))
        self.assertEqual([1, 0], list(table.matches(1)))
