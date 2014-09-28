from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import Note


class Mininote:
    def __init__(self, dev_token):
        client = EvernoteClient(token = dev_token)
        self.note_store = client.get_note_store()

    def add_note(self, text, tag_list):
        note = Note()
        note.title = "test note"
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += '<en-note>' + text + '</en-note>'
        note.tagNames = tag_list
        self.note_store.createNote(note)
