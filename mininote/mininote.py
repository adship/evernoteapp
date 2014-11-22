import logging
import re
from cgi import escape
from note import Note

from evernote.api.client import EvernoteClient
from evernote.edam.limits.constants import EDAM_NOTE_TITLE_LEN_MAX
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note as EdamNote, NoteSortOrder


logger = logging.getLogger(__name__)

class Mininote:
    def __init__(self, dev_token):
        client = EvernoteClient(token = dev_token)
        self.note_store = client.get_note_store()

    def add_note(self, text):
        """
        :param text: The note text is stored in title field
        """
        logger.debug('add note: {}'.format(text))
        note = Note(text = text)
        self.note_store.createNote(convert_to_enote(note))

    def search(self, string):
        """
        :param string: The Evernote search query string
        :returns: An iterator to retrieve notes
        """
        logger.debug('searching: {}'.format(string))
        MAX_PAGE = 1000
        note_filter = NoteFilter(words = string, order = NoteSortOrder.UPDATED, ascending = True)

        def get_page(start, count):
            result_spec = NotesMetadataResultSpec(includeTitle = True,
                                                  includeCreated = True,
                                                  includeUpdated = True)
            return self.note_store.findNotesMetadata(note_filter, start, count, result_spec)

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
        :param note: The mininote Note instance
        """
        logger.debug('update_note: {}'.format(note))
        self.note_store.updateNote(convert_to_enote(note))

    def delete_note(self, note):
        """
        :param note: The mininote Note instance
        """
        logger.debug('delete note: {}'.format(note))
        self.note_store.deleteNote(note.guid)

    def list_books(self):
        """
        :returns: List of available Evernote notebook names
        """
        notebooks = self.note_store.listNotebooks()
        return [nb.name for nb in notebooks]

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

def convert_to_enote(note):
    """
    Convert Mininote note to Evernote note
    :param note: The mininote Note instance
    """
    MAX_NOTE_LEN = EDAM_NOTE_TITLE_LEN_MAX - 2
    if len(note.text) > MAX_NOTE_LEN:
        logger.warning("Note is too long, truncating final {} characters".format(len(note.text) - MAX_NOTE_LEN))

    created = note.created_time * 1000 if note.created_time else None
    return EdamNote(guid = note.guid,
                    title = '"{}"'.format(note.text[0: MAX_NOTE_LEN]),
                    content = encode_note_text(""),
                    updated = None,
                    created = created,
                    tagNames = note.tags)
