from mock import Mock, patch
from unittest import TestCase

from mininote.n import add_note, query_edit_notes
from mininote.note import Note
from mininote.texteditor import TextEditor


class TestN(TestCase):
    """Tests for n.py"""

    @staticmethod
    def create_mock_text_editor(content):
        """
        :param str content: Fake edits to return
        """
        mock = Mock(spec=TextEditor)
        mock.edit.return_value = content
        mock.path = None
        return mock

    def setUp(self):
        """Setup notes in DB"""
        fakenote1 = Note('result1', created_time=0)
        fakenote2 = Note('result2', created_time=0)
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

    def test_query_notes(self):
        """Ensure that notes are queried correctly"""
        text_editor = self.create_mock_text_editor('')

        query_edit_notes(self.fakemn, 'search string', interactive=True, text_editor=text_editor)
        self.fakemn.search.assert_called_once_with('search string')

        # notes were sent to editor correctly
        (editor_output,),_ =  text_editor.edit.call_args
        self.assertEqual([str(self.fakenote1), str(self.fakenote2)],
                         editor_output.splitlines())

    def test_delete_note(self):
        """Ensure that deletions are synced to mininote"""
        text_editor = self.create_mock_text_editor(str(self.fakenote1)) # fakenote2 deleted)

        query_edit_notes(self.fakemn, 'search string', interactive=True, text_editor=text_editor)

        # fakenote2 was deleted 
        self.fakemn.delete_note.assert_called_once_with(self.fakenote2)

    def test_edit_note(self):
        """Ensure that edits are synced to mininote"""
        text_editor = self.create_mock_text_editor(str(self.fakenote1) + '\r\n' + \
                                                   str(self.fakenote2) + 'new content')
        query_edit_notes(self.fakemn, 'search string', interactive=True, text_editor=text_editor)

        # fakenote2 was updated
        self.fakenote2.text = self.fakenote2.text + 'new content'
        self.fakemn.update_note.assert_called_once_with(self.fakenote2)

    def test_bad_edit_note(self):
        """Ensure that bad syntax is detected and sync aborted"""
        text_editor = self.create_mock_text_editor('--bad note syntax--')
        query_edit_notes(self.fakemn, 'search string', interactive=True, text_editor=text_editor)

        # tempfile was not deleted
        self.assertFalse(text_editor.cleanup.called)

        # no updates were done
        self.assertFalse(self.fakemn.update_note.called)
        self.assertFalse(self.fakemn.delete_note.called)
