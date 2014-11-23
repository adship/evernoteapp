from mock import Mock, patch
from unittest import TestCase
from evernote.edam.notestore.ttypes import NotesMetadataList, NoteMetadata
from evernote.edam.type.ttypes import Note as EdamNote

from mininote.note import Note
from mininote.mininote import *


def fake_results_gen():
    """Generate fake search results"""
    n1 = NoteMetadata(title = 'title1', updated = 0, created = 0, guid = 101)
    n2 = NoteMetadata(title = 'title2', updated = 1000, created = 1000, guid = 102)
    yield NotesMetadataList(startIndex = 0, totalNotes = 2, notes = [n1])
    yield NotesMetadataList(startIndex = 1, totalNotes = 2, notes = [n2])

class TestMininote(TestCase):

    @patch('mininote.mininote.EvernoteClient')
    def test_add_note(self, MockEvernoteClient):
        """Ensure that server call is made to add a note"""
        client = Mininote(dev_token = 'foo')
        client.add_note(Note('bar #unittest'))

        mock_note_store = MockEvernoteClient().get_note_store()
        pargs, kwargs = mock_note_store.createNote.call_args

        self.assertEqual(['unittest'], pargs[0].tagNames)
        self.assertEqual('"bar #unittest"', pargs[0].title)

    @patch('mininote.mininote.EvernoteClient')
    def test_search(self, MockEvernoteClient):
        """Ensure that server calls are made to search for notes"""
        mock_note_store = MockEvernoteClient().get_note_store()
        mock_note_store.findNotesMetadata.side_effect = fake_results_gen()

        n1, n2 = list(Mininote(dev_token = 'foo').search('foo'))
        self.assertEqual('title1', n1.text)
        self.assertEqual(0, n1.updated_time)
        self.assertEqual('title2', n2.text)
        self.assertEqual(1, n2.updated_time)

    @patch('mininote.mininote.EvernoteClient')
    def test_update_note(self, MockEvernoteClient):
        """Ensure that server call is made to update a note"""
        mock_note_store = MockEvernoteClient().get_note_store()
        mock_note_store.findNotesMetadata.side_effect = fake_results_gen()

        client = Mininote(dev_token = 'foo')
        note = client.search('foo').next()
        note.text = 'updated title with #tag'
        client.update_note(note)

        pargs, kwargs = mock_note_store.updateNote.call_args
        self.assertEqual(['tag'], pargs[0].tagNames)
        self.assertEqual('"updated title with #tag"', pargs[0].title)

    @patch('mininote.mininote.EvernoteClient')
    def test_delete_note(self, MockEvernoteClient):
        """Ensure that server call is made to delete a note"""
        mock_note_store = MockEvernoteClient().get_note_store()
        mock_note_store.findNotesMetadata.side_effect = fake_results_gen()

        client = Mininote(dev_token = 'foo')
        n1 = client.search('foo').next()
        client.delete_note(n1)

        pargs, kwargs = mock_note_store.deleteNote.call_args
        self.assertEqual(101, pargs[0])

    def test_encode_note(self):
        """Ensure that xml characters are escaped"""
        self.assertTrue('<en-note>hello world</en-note>' in encode_note_text('hello world'))
        self.assertTrue('<en-note>&lt;div&gt;note&amp;"</en-note>' in encode_note_text('<div>note&"'))

    def test_convert_evernote(self):
        """Test that an Evernote note is converted to a Mininote note"""
        note = convert_to_enote(Note(text = '  content  ', guid = 123, created_time = 1))
        self.assertEqual(123, note.guid)
        self.assertEqual('"  content  "', note.title)
        self.assertEqual(1000, note.created)

    def test_convert_evernote_trunc(self):
        """Test that note size is truncated if too long for Evernote"""
        note = convert_to_enote(Note(text = 'x' * 1000))
        self.assertEqual('"{}"'.format('x' * 253), note.title)

    def test_convert_evernote_empty(self):
        """Test that empty note is converted"""
        note = convert_to_enote(Note(text = ''))
        self.assertEqual('""', note.title)

    def test_convert_mininote(self):
        """Test that a Mininote note is converted to an Evernote note"""
        note = convert_to_mininote(EdamNote(title = '"content"', updated = 1000, created = 1000, guid = 123))
        self.assertEqual(123, note.guid)
        self.assertEqual('content', note.text)
        self.assertEqual(1, note.created_time)
