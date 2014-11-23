from unittest import TestCase

from mininote.match_notes import match_notes, ListComparer
from mininote.note import Note


def make_notes(texts):
    return [Note(text, created_time = 0) for text in texts]

class TestDiffNote(TestCase):

    def test_diff_empty(self):
        """Ensure empty lists are handled gracefully"""
        self.assertEqual([], match_notes(make_notes([]), make_notes([])))

    def test_diff_unchanged(self):
        """Ensure unchanged notes match"""
        notes = ['Date1: Note1', 'Date2: Note2']
        self.assertEqual([(0, 0), (1, 1)], match_notes(make_notes(notes), make_notes(notes)))

    def test_diff_mod_note(self):
        """Ensure a single change is picked up"""
        before = ['Date1: Note1', 'Date2: Note2', 'Date3: Note3']
        after = ['Date1: Note1', 'Date2: edited this note', 'Date3: Note3']
        self.assertEqual([(0, 0), (1, 1), (2, 2)], match_notes(make_notes(before), make_notes(after)))

    def test_diff_multi_mode_note(self):
        """Ensure multiple changes are picked up"""
        before = ['Date1: Note1', 'Date2: Note2', 'Date3: Note3']
        after = ['Date4: changed the note and date', 'Date2: edited this note', 'Date3: Note3']
        self.assertEqual([(0, 0), (1, 1), (2, 2)], match_notes(make_notes(before), make_notes(after)))

    def test_diff_add_note(self):
        """Test that a new note is detected"""
        before = ['Date1: Note1', 'Date2: Note2']
        after = ['Date1: Note1', 'Date2: Note2', 'Date3: Note3']
        self.assertEqual([(None, 2), (0, 0), (1, 1)], sorted(match_notes(make_notes(before), make_notes(after))))

    def test_diff_multi_add_note(self):
        """Test that previous note is matched when many notes are added"""
        before = ['note C']
        after = ['note A', 'note B', 'note C', 'note D']
        self.assertEqual([(None, 0), (None, 1), (None, 3), (0, 2)], sorted(match_notes(make_notes(before), make_notes(after))))

    def test_diff_delete_note(self):
        """Test that a deleted note is detected"""
        before = ['Date1: Note1', 'Date2: Note2', 'Date3: Note3']
        after = ['Date2: Note2', 'Date3: Note3']
        self.assertEqual([(0, None), (1, 0), (2, 1)], sorted(match_notes(make_notes(before), make_notes(after))))

    def test_diff_multi_delete_note(self):
        """Test that remaining note is found when many notes are deleted"""
        before = ['note A', 'note B', 'note C', 'note D']
        after = ['note C']
        self.assertEqual([(0, None), (1, None), (2, 0), (3, None)], sorted(match_notes(make_notes(before), make_notes(after))))

    def test_diff_identical_notes(self):
        """Ensure no changes are detected if all notes are identical"""
        notes = ['note', 'note', 'note', 'note']
        self.assertEqual([(0, 0), (1, 1), (2, 2), (3, 3)],match_notes(make_notes(notes), make_notes(notes)))

    def test_diff_change_date(self):
        """Ensure that notes with modified dates are treated as new notes"""
        before = [Note('foo', created_time = 0), Note('bar', created_time = 1)]
        after = [Note('foo', created_time = 0), Note('bar', created_time = 2)]
        self.assertEqual([(0, 0), (None, 1), (1, None)], match_notes(before, after))

    def test_adds_first(self):
        """Ensure that additions come before deletions in pairs list"""
        before = [Note('foo', created_time = 0)]
        after = [Note('foo', created_time = 1)]
        self.assertEqual([(None, 0), (0, None)], match_notes(before, after))

def scorefunc(item1, item2):
    return -abs(item1 - item2)

def keyfunc(item):
    return 0

class TestListComparer(TestCase):

    def test_get_score(self):
        table = ListComparer([0, 1], [0, 2], keyfunc, scorefunc)

        self.assertEqual(0, table.score(0, 0))
        self.assertEqual(-1, table.score(1, 1))

        self.assertEqual(-1, table.score(1, 0))
        self.assertEqual(-2, table.score(0, 1))

    def test_get_inexact_matches(self):
        table = ListComparer([0, 1], [0.1, 1.1], keyfunc, scorefunc)

        self.assertEqual([0, 1], list(table.best_matches(0)))
        self.assertEqual([1, 0], list(table.best_matches(1)))

    def test_get_exact_matches(self):
        table = ListComparer([0, 1], [0, 1], keyfunc, scorefunc)

        self.assertEqual([0, 1], list(table.best_matches(0)))
        self.assertEqual([1, 0], list(table.best_matches(1)))
