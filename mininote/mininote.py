import logging
from cgi import escape
from note import Note

from evernote.api.client import EvernoteClient
from evernote.edam.limits.constants import EDAM_NOTE_TITLE_LEN_MIN, EDAM_NOTE_TITLE_LEN_MAX
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note as EdamNote, NoteSortOrder


logger = logging.getLogger(__name__)

def encode_note(text):
    template = '''<?xml version="1.0" encoding="UTF-8"?>
                  <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
                  <en-note>{0}</en-note>'''
    return template.format(escape(text))

def create_note(note_metadata):
    """
    :param note_metadata: NoteMetadata instance
    """
    return Note(note_metadata.title, updated_time = note_metadata.updated / 1000)

class Mininote:
    def __init__(self, dev_token):
        client = EvernoteClient(token = dev_token)
        self.note_store = client.get_note_store()

    def add_note(self, text, tag_list):
        """
        :param text: The note text is stored in title field
        :param tag_list: A list of tag strings to attach to note
        """
        note = EdamNote()
        if len(text) < EDAM_NOTE_TITLE_LEN_MIN or text.isspace():
            note.title = "untitled"
        elif len(text) > EDAM_NOTE_TITLE_LEN_MAX:
            note.title = text[0:EDAM_NOTE_TITLE_LEN_MAX]
            logger.warning("The text is too long, cutting off...")
        else:
            note.title = text                
        note.content = encode_note("")
        note.tagNames = tag_list
        self.note_store.createNote(note)

    def search(self, string):
        """
        :param string: The Evernote search query string
        :returns: An iterator to retrieve notes
        """
        MAX_PAGE = 1000
        note_filter = NoteFilter(words = string, order = NoteSortOrder.UPDATED, ascending = True)

        def get_page(start, count):
            result_spec = NotesMetadataResultSpec(includeTitle = True, includeUpdated = True)
            return self.note_store.findNotesMetadata(note_filter, start, count, result_spec)

        i = 0
        page = get_page(0, MAX_PAGE)
        while i < page.totalNotes:
            for note_meta in page.notes:
                yield create_note(note_meta)
            i += len(page.notes)
            if i < page.totalNotes: 
                page = get_page(i, MAX_PAGE)

    def list_books(self):
        notebooks = self.note_store.listNotebooks()
        for nb in notebooks:
            print nb.name
