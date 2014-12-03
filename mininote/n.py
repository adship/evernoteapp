#!/usr/bin/env python
import argparse
import logging

from config_store import ConfigStore, ConfigLoadError
from match_notes import match_notes
from mininote import Mininote
from note import Note, NoteParseError
from oauth import get_auth_token
from texteditor import TextEditor


logger = logging.getLogger(__name__)

def login(config_store):
    """
    Run through oauth procedure and store authenticaion token

    :param ConfigStore config_store: Store for authentication token
    """
    config_store.auth_token = get_auth_token()

def add_note(mn, note_string = None):
    """
    Save a new note.

    :param mn: Mininote instance
    :param note_string: Note to add. If not provided, will prompt for note.
    """
    if note_string == None:
        note_string = raw_input('mininote>')
    mn.add_note(Note(note_string))

def query_edit_notes(mn, query_string, interactive):
    """
    Display search results and allow edits.

    :param mn: Mininote instance
    :param query_string: Search string
    :param interactive: if True, display results in text editor
                        and allow edits to be made
    """
    before_notes = list(mn.search(query_string))
    before_formatted_notes = '\r\n'.join(map(str, before_notes))

    if not interactive:
        print before_formatted_notes
    else:
        editor = TextEditor(before_formatted_notes)

        after_formatted_notes = editor.edit()
        try:
            nonblank_lines = filter(lambda line: len(line.strip()) > 0, after_formatted_notes.splitlines())
            after_notes = map(Note.parse_from_str, nonblank_lines)
        except NoteParseError:
            logger.error("Unable to parse changes to notes. Session is saved in {}".format(editor.path))
            return
        editor.cleanup()

        before_notes_reparsed = map(lambda n: Note.parse_from_str(str(n)), before_notes)
        pairs = match_notes(before_notes_reparsed, after_notes)
        for before, after in pairs:
            if before == None:
                mn.add_note(after_notes[after])
            elif after == None:
                mn.delete_note(before_notes[before])
            elif after_notes[after].text != before_notes[before].text:
                before_notes[after].text = after_notes[after].text
                mn.update_note(before_notes[after])

def list_all_books(mn):
    """
    Get a list of Evernote notebooks.

    :param mn: Mininote instance
    """
    for notebook in mn.list_books():
        print notebook

if __name__ == '__main__':
    root_logger = logging.getLogger()
    root_logger.setLevel('WARNING')
    root_logger.addHandler(logging.StreamHandler())

    parser = argparse.ArgumentParser()
    parser.add_argument("note_text", default=None, nargs="?")
    parser.add_argument("-a", "--authenticate", help="prompt for authentication credentials", action="store_true")
    parser.add_argument("-c", "--change-notebook", help="change the default notebook")
    parser.add_argument("-b", "--list-books", help="list all notebooks", dest = "list_books", action="store_true")
    parser.add_argument("-q", "--query", help="query server for note containing the string")
    parser.add_argument("-v", "--verbose", help="display additional information", action="store_true")
    parser.add_argument("-i", "--interactive", default = False, help="interactive edit mode", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        root_logger.setLevel('DEBUG')

    config_store = ConfigStore()
    if args.authenticate:
        login(config_store)

    try:
        auth_token = config_store.auth_token
    except ConfigLoadError:
        logger.error('Please login using "n --authenticate"')
        auth_token = None

    if auth_token:
        mn = Mininote(auth_token)
        if args.change_notebook:
            logger.error("change notebook feature not implemented yet...")
        elif args.query:
            query_edit_notes(mn, args.query, args.interactive)
        elif args.list_books:
            list_all_books(mn)
        else:
            add_note(mn, args.note_text)
