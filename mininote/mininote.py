from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import Note
import re


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


def get_tags(note):
    return re.findall(r"#(\w+)", note)



if __name__ == '__main__':
    dev_token = "your dev token here"
    mn = Mininote(dev_token)

    note = "this is a #test #note"
    mn.add_note(note, get_tags(note))

    print get_tags(note)
    print get_tags('test tags #mini #Mini')
