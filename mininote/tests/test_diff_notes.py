from unittest import TestCase
from mininote.diff_notes import diff_notes
from mininote.note import Note


def make_notes(texts):
    return [Note(text) for text in texts]

class TestDiffNote(TestCase):

    def test_diff_empty(self):
        """Ensure empty lists are handled gracefully"""
        self.assertEqual([], diff_notes(make_notes([]), make_notes([])))

    def test_diff_unchanged(self):
        """Ensure unchanged notes match"""
        notes = ['Date1: Note1', 'Date2: Note2']
        self.assertEqual([(0, 0), (1, 1)], diff_notes(make_notes(notes), make_notes(notes)))

    def test_diff_mod_note(self):
        """Ensure a single change is picked up"""
        before = ['Date1: Note1', 'Date2: Note2', 'Date3: Note3']
        after = ['Date1: Note1', 'Date2: edited this note', 'Date3: Note3']
        self.assertEqual([(0, 0), (1, 1), (2, 2)], diff_notes(make_notes(before), make_notes(after)))

    def test_diff_multi_mode_note(self):
        """Ensure multiple changes are picked up"""
        before = ['Date1: Note1', 'Date2: Note2', 'Date3: Note3']
        after = ['Date4: changed the note and date', 'Date2: edited this note', 'Date3: Note3']
        self.assertEqual([(0, 0), (1, 1), (2, 2)], diff_notes(make_notes(before), make_notes(after)))

    def test_diff_add_note(self):
        """Test that a new note is detected"""
        before = ['Date1: Note1', 'Date2: Note2']
        after = ['Date1: Note1', 'Date2: Note2', 'Date3: Note3']
        self.assertEqual([(None, 2), (0, 0), (1, 1)], diff_notes(make_notes(before), make_notes(after)))

    def test_diff_multi_add_note(self):
        """Test that previous note is matched when many notes are added"""
        before = ['note C']
        after = ['note A', 'note B', 'note C', 'note D']
        self.assertEqual([(None, 0), (None, 1), (None, 3), (0, 2)], diff_notes(make_notes(before), make_notes(after)))

    def test_diff_delete_note(self):
        """Test that a deleted note is detected"""
        before = ['Date1: Note1', 'Date2: Note2', 'Date3: Note3']
        after = ['Date2: Note2', 'Date3: Note3']
        self.assertEqual([(0, None), (1, 0), (2, 1)], diff_notes(make_notes(before), make_notes(after)))

    def test_diff_multi_delete_note(self):
        """Test that remaining note is found when many notes are deleted"""
        before = ['note A', 'note B', 'note C', 'note D']
        after = ['note C']
        self.assertEqual([(0, None), (1, None), (2, 0), (3, None)], diff_notes(make_notes(before), make_notes(after)))

    def test_diff_identical_notes(self):
        """Ensure no changes are detected if all notes are identical"""
        notes = ["note", "note", "note"]
        self.assertEqual([(0, 0), (1, 1), (2, 2)],diff_notes(make_notes(notes), make_notes(notes)))
