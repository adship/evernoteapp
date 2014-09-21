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

if __name__ == '__main__':
    dev_token = "S=s1:U=8f3c2:E=14f3d61c864:C=147e5b099f0:P=1cd:A=en-devtoken:V=2:H=86cf060ac57d976f657e23eb6f587c3f"
    mn = Mininote(dev_token)

    note = "this is a #test #note"
    mn.add_note(note, ['test', 'note'])
