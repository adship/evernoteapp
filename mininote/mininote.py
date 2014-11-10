import logging
import re
from cgi import escape
from note import Note

from evernote.api.client import EvernoteClient
from evernote.edam.limits.constants import EDAM_NOTE_TITLE_LEN_MIN, EDAM_NOTE_TITLE_LEN_MAX
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
            result_spec = NotesMetadataResultSpec(includeTitle = True, includeUpdated = True)
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
    return Note(text = note_metadata.title,
                updated_time = note_metadata.updated / 1000,
                guid = note_metadata.guid)

def convert_to_enote(note):
    """
    Convert Mininote note to Evernote note
    :param note: The mininote Note instance
    """
    if len(note.text) < EDAM_NOTE_TITLE_LEN_MIN or note.text.isspace():
        title = "untitled"
    elif len(note.text) > EDAM_NOTE_TITLE_LEN_MAX:
        title = note.text[0:EDAM_NOTE_TITLE_LEN_MAX]
        logger.warning("The text is too long, cutting off...")
    else:
        title = note.text
    updated = note.updated_time * 1000 if note.updated_time else None
    return EdamNote(guid = note.guid,
                    title = title,
                    content = encode_note_text(""),
                    updated = updated,
                    tagNames = note.tags)
