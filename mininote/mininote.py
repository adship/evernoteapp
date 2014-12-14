import logging
import re
from cgi import escape
from constants import EVERNOTE_NOTEBOOK
from note import Note

from evernote.api.client import EvernoteClient
from evernote.edam.limits.constants import EDAM_NOTE_TITLE_LEN_MAX
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note as EdamNote, Notebook, NoteSortOrder


logger = logging.getLogger(__name__)

class Mininote:
    """Provides access to the Evernote 'database'."""

    def __init__(self, token, notebook_guid=None):
        """
        :param str token: The Evernote auth token
        :param str notebook_guid: The Evernote notebook GUID or None if not known
        """
        client = EvernoteClient(token=token)
        self._note_store = client.get_note_store()
        self.notebook_guid = notebook_guid or self._get_create_notebook()

    def add_note(self, note):
        """
        :param Note note: The mininote Note instance
        """
        logger.debug('add note: {}'.format(note.text))
        self._note_store.createNote(convert_to_enote(note, self.notebook_guid))

    def search(self, string):
        """
        :param str string: The Evernote search query string
        :returns: An iterator to retrieve notes
        """
        logger.debug('searching: {}'.format(string))
        MAX_PAGE = 1000
        note_filter = NoteFilter(words=string,
                                 notebookGuid=self.notebook_guid,
                                 order=NoteSortOrder.UPDATED,
                                 ascending=True)

        def get_page(start, count):
            result_spec = NotesMetadataResultSpec(includeTitle=True,
                                                  includeCreated=True,
                                                  includeUpdated=True)
            return self._note_store.findNotesMetadata(note_filter, start, count, result_spec)

        i = 0
        page = get_page(0, MAX_PAGE)
        while i < page.totalNotes:
            for note_meta in page.notes:
                yield convert_to_mininote(note_meta)
            i += len(page.notes)
            if i < page.totalNotes: 
                page = get_page(i, MAX_PAGE)

    def update_note(self, note):
        """
        :param Note note: The mininote Note instance
        """
        logger.debug('update_note: {}'.format(note))
        self._note_store.updateNote(convert_to_enote(note, self.notebook_guid))

    def delete_note(self, note):
        """
        :param Note note: The mininote Note instance
        """
        logger.debug('delete note: {}'.format(note))
        self._note_store.deleteNote(note.guid)

    def _get_create_notebook(self):
        """
        Get or create the Evernote notebook.

        :returns: Notebook guid
        """
        for notebook in self._note_store.listNotebooks():
            if notebook.name == EVERNOTE_NOTEBOOK:
                return notebook.guid
        return self._note_store \
                   .createNotebook(Notebook(name=EVERNOTE_NOTEBOOK)) \
                   .guid

def encode_note_text(text):
    template = '''<?xml version="1.0" encoding="UTF-8"?>
                  <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
                  <en-note>{0}</en-note>'''
    return template.format(escape(text))

def convert_to_mininote(note_metadata):
    """
    Convert Evernote note to Mininote note
    :param note_metadata: NoteMetadata instance
    """
    if len(note_metadata.title) > 2 and note_metadata.title.startswith('"') and \
                                        note_metadata.title.endswith('"'):
        text = note_metadata.title[1: -1]
    else:
        text = note_metadata.title
    return Note(text = text,
                updated_time = note_metadata.updated / 1000,
                created_time = note_metadata.created / 1000,
                guid = note_metadata.guid)

def convert_to_enote(note, notebook_guid=None):
    """
    Convert Mininote note to Evernote note
    :param note: The mininote Note instance
    """
    MAX_NOTE_LEN = EDAM_NOTE_TITLE_LEN_MAX - 2
    if len(note.text) > MAX_NOTE_LEN:
        logger.warning("Note is too long, truncating final {} characters".format(len(note.text) - MAX_NOTE_LEN))

    created = note.created_time * 1000 if note.created_time else None
    return EdamNote(guid = note.guid,
                    notebookGuid = notebook_guid,
                    title = '"{}"'.format(note.text[0: MAX_NOTE_LEN]),
                    content = encode_note_text(""),
                    updated = None,
                    created = created,
                    tagNames = note.tags)
