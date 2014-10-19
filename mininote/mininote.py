from cgi import escape
from xml.dom import minidom

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note as EdamNote, NoteSortOrder


def encode_note(text):
    template = '''<?xml version="1.0" encoding="UTF-8"?>
                  <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
                  <en-note>{0}</en-note>'''
    return template.format(escape(text))

class Note:
    def __init__(self, note_meta):
        """
        :param note_meta: NoteMetadata instance
        """
        self.text = note_meta.title
        self.updated_time = note_meta.updated / 1000

class Mininote:
    def __init__(self, dev_token):
        client = EvernoteClient(token = dev_token)
        self.note_store = client.get_note_store()

    def add_note(self, text, tag_list):
        """
        :param text: The note text to store
        :param tag_list: A list of tag strings to attach to note
        """
        note = EdamNote()
        note.title = "test note"
        note.content = encode_note(text)
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
                yield Note(note_meta)
            i += len(page.notes)
            if i < page.totalNotes: 
                page = get_page(i, MAX_PAGE)

    def list_books(self):
        notebooks = self.note_store.listNotebooks()
        for nb in notebooks:
            print nb.name

    def list_notes(self):
        pass
