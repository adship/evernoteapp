#!/usr/bin/env python
import argparse
import logging
import os
import platform
import re
from datetime import datetime

from mininote import Mininote


logger = logging.getLogger(__name__)

def get_tags(note):
    """
    # gets the tag of the note in the format of
    :param note: in the format of "my note is #tag1 #tag2"
    """
    return re.findall(r"#(\w+)", note)

def get_note_text():
    # user enters the note with tag at command prompt
    return raw_input('mininote>')

def get_token():
    # gets the authentication token -- dev_token for now
    # TODO: add support for 'real' token
    windows = "Windows" in platform.system()
    my_environ = os.environ.copy()

    if windows:
        path_default = os.path.join(my_environ["USERPROFILE"], "AppData", "Roaming", "mininote")
    else:
        path_default = os.path.join(my_environ["HOME"], ".mininote")
    logger.info("getting token from default path: {}".format(path_default))

    try:
        file_name = os.path.join(path_default, "EvernoteDevToken.txt")
        theFile = open(file_name, 'rb')
    except:
        logger.error("unable to open token file" + file_name)
        return

    theString = theFile.read()
    return theString.strip()

def add_note(token, note_string):
    mn = Mininote(token)
    if note_string == '':
        note_string = get_note_text()
    note_tags = get_tags(note_string)
    mn.add_note(note_string, note_tags)

def query_notes(token, query_string):
    mn = Mininote(token)
    for note in mn.search(query_string):
        date = datetime.fromtimestamp(note.updated_time).strftime("%x %I:%M %p")
        print u'{}: {}'.format(date, note.text)

def list_all_notes(token):
    logger.info("list_all_notes feature not implemented yet...")
    mn = Mininote(token)
    mn.list_notes()

def list_all_books(token):
    mn = Mininote(token)
    mn.list_books()

if __name__ == '__main__':
    root_logger = logging.getLogger()
    root_logger.setLevel('INFO')
    root_logger.addHandler(logging.StreamHandler())

    parser = argparse.ArgumentParser()
    parser.add_argument("note_text", default="", nargs="?")
    parser.add_argument("-a", "--authenticate", help="prompt for authentication credentials", action="store_true")
    parser.add_argument("-c", "--change-notebook", help="change the default notebook")
    parser.add_argument("-b", "--list-books", help="list all notebooks", dest = "list_books", action="store_true")
    parser.add_argument("-n", "--list-notes", help="list all notes in the default notebook", dest = "list_notes", action="store_true")
    parser.add_argument("-q", "--query", help="query server for note containing the string")
    parser.add_argument("-v", "--verbose", help="display additional information", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        root_logger.setLevel('DEBUG')

    token = get_token()
    if token:
        if args.change_notebook:
            logger.info("change notebook feature not implemented yet...")
        elif args.query:
            query_notes(token, args.query)
        elif args.list_books:
            list_all_books(token)
        elif args.list_notes:
            list_all_notes(token)
        else:
            add_note(token, args.note_text)

