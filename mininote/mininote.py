from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter
from evernote.edam.notestore.ttypes import NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note


class Mininote:
    def __init__(self, dev_token):
        client = EvernoteClient(token = dev_token)
        self.note_store = client.get_note_store()

    def add_note(self, text, tag_list):
        """
        :param text: The note text to store
        :param tag_list: A list of tag strings to attach to note
        """
        note = Note()
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
        note_filter = NoteFilter(words = string)

        def get_notes(start, count):
            return self.note_store.findNotesMetadata(note_filter, start, count, NotesMetadataResultSpec())

        i = 0
        page = get_notes(0, MAX_PAGE)
        while i < page.totalNotes:
            for note in page.notes:
                yield self.note_store.getNote(note.guid, True, False, False, False).content

            i += len(page.notes)
            page = get_notes(i, MAX_PAGE)
