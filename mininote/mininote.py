from xml.dom import minidom

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note as EdamNote, NoteSortOrder


def decode_note(note_xml):
    """
    :param string: The Evernote string in xml format
    :returns: A decoded note text
    """
    xml_str = minidom.parseString(note_xml)
    return xml_str.childNodes[1].firstChild.data

class Note:
    def __init__(self, edam_note):
        """
        :param edam_note: The EdamNote instance
        """
        self.text = decode_note(edam_note.content)
        self.updated_time = edam_note.updated / 1000

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
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += '<en-note>' + text + '</en-note>'
        note.tagNames = tag_list
        self.note_store.createNote(note)

    def search(self, string):
        """
        :param string: The Evernote search query string
        :returns: An iterator to retrieve notes
        """
        MAX_PAGE = 1000
        note_filter = NoteFilter(words = string, order = NoteSortOrder.UPDATED, ascending = True)

        def get_notes(start, count):
            return self.note_store.findNotesMetadata(note_filter, start, count, NotesMetadataResultSpec())

        i = 0
        page = get_notes(0, MAX_PAGE)
        while i < page.totalNotes:
            for note_meta in page.notes:
                edam_note = self.note_store.getNote(note_meta.guid, True, False, False, False)
                yield Note(edam_note)
            i += len(page.notes)
            page = get_notes(i, MAX_PAGE)

    def list_books(self):
        notebooks = self.note_store.listNotebooks()
        for nb in notebooks:
            print nb.name

    def list_notes(self):
        pass
