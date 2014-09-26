from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import Note
import re
import os
import platform
import argparse

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

def get_token():
    # gets the authentication token -- dev_token for now
    # TODO: add support for 'real' token
    windows = "Windows" in platform.system()
    my_environ = os.environ.copy()

    if windows:
        path_default = my_environ["USERPROFILE"] + "\\"
        print "getting token from default Windows path: " + path_default
    else:
        path_default = "~/.mininote/"
        print "getting token from default Linux path: " + path_default

    try:
        file_name = path_default + "EvernoteDevToken.txt"
        theFile = open(file_name, 'rb')
    except:
        print "unable to open token file" + file_name
        return

    theString = theFile.read()
    return theString.strip()


if __name__ == '__main__':
    try:
        token = get_token()
    except:
        print "could not read token"
    if token:
        mn = Mininote(token)

        note = "this is a #test #note"
        mn.add_note(note, get_tags(note))

        print get_tags(note)
        print get_tags('test tags #mini #Mini')


