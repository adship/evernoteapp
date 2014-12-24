from mock import Mock, patch
from unittest import TestCase
from evernote.edam.notestore.ttypes import NotesMetadataList, NoteMetadata
from evernote.edam.type.ttypes import Note as EdamNote, Notebook

from mininote.note import Note
from mininote.mininote import *


class MockMininote(Mininote):

    def __init__(self, token, **kwargs):
        fake_notes = NotesMetadataList(startIndex=0, totalNotes=0, notes=[])
        fake_notebooks = []
        note_store = Mock()
        note_store.listNotebooks.return_value = kwargs.get('fake_notebooks', fake_notebooks)
        note_store.findNotesMetadata.return_value = kwargs.get('fake_notes', fake_notes)
        note_store.getNote.return_value = kwargs.get('fake_get_note', None)
        note_store.createNotebook.return_value = Notebook(guid='notebook-guid')
        self.note_store = note_store
        super(MockMininote, self).__init__(token)

    def _note_store(self):
        return self.note_store

def fake_notes():
    n1 = NoteMetadata(title='title1', updated=0, created=0, guid=101)
    n2 = NoteMetadata(title='title2', updated=1000, created=1000, guid=102)
    return NotesMetadataList(startIndex=0, totalNotes=1, notes=[n1, n2])

class TestMininoteEvernoteInteraction(TestCase):
    """Test interaction with Evernote"""

    @patch('mininote.mininote.EvernoteClient')
    def test_get_notebook(self, MockEvernoteClient):
        """Ensure that notebook is found if not provided"""
        fake_notebooks = [Notebook(name='mininote', guid='existing-guid')]
        client = MockMininote(token='foo', fake_notebooks=fake_notebooks)
        self.assertEqual('existing-guid', client.notebook_guid)

    @patch('mininote.mininote.EvernoteClient')
    def test_create_notebook(self, MockEvernoteClient):
        """Ensure that notebook is created if does not exist"""
        client = MockMininote(token='foo')
        self.assertEqual('notebook-guid', client.notebook_guid)

    @patch('mininote.mininote.EvernoteClient')
    def test_add_note(self, MockEvernoteClient):
        """Ensure that server call is made to add a note"""
        client = MockMininote(token='foo')
        client.add_note(Note('bar #unittest'))

        pargs, kwargs = client._note_store().createNote.call_args

        self.assertEqual(['unittest'], pargs[0].tagNames)
        self.assertEqual('"bar #unittest"', pargs[0].title)
        self.assertEqual(encode_note_text('bar #unittest'), pargs[0].content)

    @patch('mininote.mininote.EvernoteClient')
    def test_search(self, MockEvernoteClient):
        """Ensure that server calls are made to search for notes"""
        n1, n2 = list(MockMininote(token='foo', fake_notes=fake_notes()).search('foo'))
        self.assertEqual('title1', n1.text)
        self.assertEqual(0, n1.updated_time)
        self.assertEqual('title2', n2.text)
        self.assertEqual(1, n2.updated_time)

    @patch('mininote.mininote.EvernoteClient')
    def test_search_long_note(self, MockEvernoteClient):
        """Ensure that full note is retrieved if content cannot fit in title"""
        n1 = NoteMetadata(guid=101, contentLength=2000, created=0, updated=0)
        page = NotesMetadataList(startIndex=0, totalNotes=1, notes=[n1])

        fake_note = EdamNote(title='title', content='<en-note>content</en-note>')
        client = MockMininote(token='foo', fake_notes=page, fake_get_note=fake_note)
        result = client.search('something').next()
        self.assertEqual('content', result.text)

    @patch('mininote.mininote.EvernoteClient')
    def test_update_note(self, MockEvernoteClient):
        """Ensure that server call is made to update a note"""
        client = MockMininote(token='foo', fake_notes=fake_notes())
        note = client.search('foo').next()
        note.text = 'updated title with #tag'
        client.update_note(note)

        pargs, kwargs = client.note_store.updateNote.call_args
        self.assertEqual(['tag'], pargs[0].tagNames)
        self.assertEqual('"updated title with #tag"', pargs[0].title)

    @patch('mininote.mininote.EvernoteClient')
    def test_delete_note(self, MockEvernoteClient):
        """Ensure that server call is made to delete a note"""
        client = MockMininote(token='foo', fake_notes=fake_notes())

        n1 = client.search('foo').next()
        client.delete_note(n1)

        pargs, kwargs = client.note_store.deleteNote.call_args
        self.assertEqual(101, pargs[0])

class TestMininoteUtilities(TestCase):
    """Test mininote utilities"""

    def test_decode_note(self):
        """Ensure that content is extracted"""
        note1 = """<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
            <en-note>&lt;hello&gt;</en-note>"""
        self.assertEquals('<hello>', decode_note_text(note1))

        note2 = """<?xml version="1.0" encoding="UTF-8"?>
                   <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
                   <en-note>
                      <h2>Enumerations</h2>
                      <div>
                         <h3>Enumeration: PrivilegeLevel</h3>
                         This enumeration defines the possible permission levels for a user. Free accounts will have a level of NORMAL and paid Premium accounts will have a level of PREMIUM. <br clear="none"/><br clear="none"/>
                         <table>
                            <tr>
                               <td colspan="1" rowspan="1"><code>NORMAL</code></td>
                               <td colspan="1" rowspan="1"><code>1</code></td>
                            </tr>
                         </table>
                      </div>
                      <div><br clear="none"/></div>
                      <div><br clear="none"/></div>
                   </en-note>
                   """
        self.assertEquals('EnumerationsEnumeration: PrivilegeLevelThis enumeration defines the possible permission levels for a user. Free accounts will have a level of NORMAL and paid Premium accounts will have a level of PREMIUM.NORMAL1', decode_note_text(note2))

    def test_encode_note(self):
        """Ensure that xml characters are escaped"""
        self.assertTrue('<en-note>hello world</en-note>' in encode_note_text('hello world'))
        self.assertTrue('<en-note>&lt;div&gt;note&amp;"</en-note>' in encode_note_text('<div>note&"'))

    def test_convert_evernote(self):
        """Test that an Evernote note is converted to a Mininote note"""
        note = convert_to_enote(Note(text='  content  ', guid=123, created_time=1),
                                notebook_guid='guid')
        self.assertEqual(123, note.guid)
        self.assertEqual('"  content  "', note.title)
        self.assertEqual(1000, note.created)
        self.assertEqual('guid', note.notebookGuid)

    def test_convert_evernote_trunc(self):
        """Test that note size is truncated if too long for Evernote"""
        note = convert_to_enote(Note(text='x' * 1000))
        self.assertEqual('"{}"'.format('x' * 253), note.title)

    def test_convert_evernote_empty(self):
        """Test that empty note is converted"""
        note = convert_to_enote(Note(text=''))
        self.assertEqual('""', note.title)

    def test_convert_mininote(self):
        """Test that a note is converted to Mininote format"""
        note = convert_to_mininote(NoteMetadata(title='"content"', updated=1000, created=1000, guid=123), None)
        self.assertEqual(123, note.guid)
        self.assertEqual('content', note.text)
        self.assertEqual(1, note.created_time)

    def test_convert_mininote_empty_note(self):
        """Test that an empty note is converted to Mininote format"""
        note = convert_to_mininote(NoteMetadata(title='""', updated=1000, created=1000), None)
        self.assertEqual('', note.text)

    def test_convert_mininote_long_note(self):
        """Test that a long note is converted to Mininote format"""
        note = convert_to_mininote(NoteMetadata(title='""', updated=1000, created=1000),
                                   EdamNote(content=encode_note_text('longer note')))
        self.assertEqual('longer note', note.text)
