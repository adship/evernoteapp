from mock import Mock, patch
from unittest import TestCase

from mininote.n import add_note, query_edit_notes
from mininote.note import Note


class TestN(TestCase):
    """Tests for n.py"""

    def setUp(self):
        """Setup notes in DB"""
        fakenote1 = Note('result1', created_time = 0)
        fakenote2 = Note('result2', created_time = 0)
        fakemn = Mock()
        fakemn.search.return_value = iter([fakenote1, fakenote2])

        self.fakenote1 = fakenote1
        self.fakenote2 = fakenote2
        self.fakemn = fakemn

    def test_add_note(self):
        """Ensure that new note is passed to Mininote"""
        add_note(self.fakemn, 'string')

        (note,),_ = self.fakemn.add_note.call_args
        self.assertEqual('string', note.text)

    @patch('mininote.n.TextEditor')
    def test_query_notes(self, TextEditor):
        """Ensure that notes are queried correctly"""
        query_edit_notes(self.fakemn, 'search string', interactive = True)
        self.fakemn.search.assert_called_once_with('search string')

        # notes were sent to editor correctly
        (editor_output,),_ = TextEditor.call_args
        self.assertEqual([str(self.fakenote1), str(self.fakenote2)],
                         editor_output.splitlines())

    @patch('mininote.n.TextEditor')
    def test_delete_note(self, TextEditor):
        """Ensure that deletions are synced to mininote"""
        TextEditor().edit.return_value = str(self.fakenote1) # fakenote2 deleted

        query_edit_notes(self.fakemn, 'search string', interactive = True)

        # fakenote2 was deleted 
        self.fakemn.delete_note.assert_called_once_with(self.fakenote2)

    @patch('mininote.n.TextEditor')
    def test_edit_note(self, TextEditor):
        """Ensure that edits are synced to mininote"""
        TextEditor().edit.return_value = str(self.fakenote1) + '\r\n' + \
                                         str(self.fakenote2) + 'new content'

        query_edit_notes(self.fakemn, 'search string', interactive = True)

        # fakenote2 was updated
        self.fakenote2.text = self.fakenote2.text + 'new content'
        self.fakemn.update_note.assert_called_once_with(self.fakenote2)

    @patch('mininote.n.TextEditor')
    def test_bad_edit_note(self, TextEditor):
        """Ensure that bad syntax is detected and sync aborted"""
        TextEditor().edit.return_value = '--bad note syntax--'

        query_edit_notes(self.fakemn, 'search string', interactive = True)

        # tempfile was not deleted
        self.assertFalse(TextEditor().cleanup.called)

        # no updates were done
        self.assertFalse(self.fakemn.update_note.called)
        self.assertFalse(self.fakemn.delete_note.called)
