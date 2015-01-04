#!/usr/bin/env python
import argparse
import colorama
import logging
import time

from collections import Counter
from colorstr import colorstr
from config_store import ConfigStore, ConfigLoadError
from match_notes import match_notes
from mininote import Mininote
from note import Note, NoteParseError
from oauth import get_auth_token
from texteditor import TextEditor, TextEditorError


logger = logging.getLogger(__name__)

def login(config_store):
    """
    Run through oauth procedure and store authentication token.

    :param ConfigStore config_store: Store for authentication token
    """
    config_store.delete_auth()
    config_store.auth_token = get_auth_token()

def add_note(mn, note_string=None):
    """
    Save a new note.

    :param Mininote mn: Mininote instance
    :param str note_string: Note to add. If not provided, will prompt for note.
    """
    if note_string is None:
        note_string = raw_input(colorstr('DIM', 'mn> '))
    mn.add_note(Note(note_string))

def query_notes(mn, query_string):
    """
    Display search results.

    :param Mininote mn: Mininote instance
    :param string query_string: Search string
    """
    INLINE_TAG_STYLE = 'BRIGHT-CYAN'
    INLINE_DATE_STYLE = 'MAGENTA'
    TAGLIST_TAG_STYLE = 'BRIGHT-CYAN'
    TAGLIST_COUNT_STYLE = 'DIM'

    def colorize(word):
        if word.startswith('#'):
            return colorstr(INLINE_TAG_STYLE, word)
        else:
            return word

    time0 = time.time()
    tagcounts = Counter()
    for note in mn.search(query_string):
        tagcounts.update(note.tags)
        colordate = colorstr(INLINE_DATE_STYLE, '{}: '.format(note.strft_created_time))
        colortext = ' '.join(map(colorize, note.text.split(' ')))
        print(colordate + colortext)

    if len(tagcounts) > 0:
        print('\n' + ' '.join([colorstr(TAGLIST_TAG_STYLE, '#{}'.format(tag)) +
                               colorstr(TAGLIST_COUNT_STYLE, ' ({}) '.format(count))
                               for tag, count
                               in sorted(tagcounts.items(), key=lambda p:p[1], reverse=True)]))

    logger.debug('Total search/display time: {}'.format(time.time()-time0))

def edit_notes(mn, query_string, text_editor):
    """
    Display search results and allow edits.

    :param Mininote mn: Mininote instance
    :param string query_string: Search string
    :param TextEditor text_editor: Editor for interactive edit mode
    """
    before_notes = list(mn.search(query_string))
    before_formatted_notes = '\r\n'.join(map(str, before_notes))
    after_formatted_notes = text_editor.edit(before_formatted_notes)

    try:
        nonblank_lines = filter(lambda line: len(line.strip()) > 0, after_formatted_notes.splitlines())
        after_notes = map(Note.parse_from_str, nonblank_lines)
    except NoteParseError:
        logger.error("Unable to parse changes to notes. Session is saved in {}".format(text_editor.path))
        return
    text_editor.cleanup()

    before_notes_reparsed = map(lambda n: Note.parse_from_str(str(n)), before_notes)
    pairs = match_notes(before_notes_reparsed, after_notes)
    for before, after in pairs:
        if before is None:
            mn.add_note(after_notes[after])
        elif after is None:
            mn.delete_note(before_notes[before])
        elif after_notes[after].text != before_notes[before].text:
            before_notes[after].text = after_notes[after].text
            mn.update_note(before_notes[after])

def main():
    colorama.init()

    root_logger = logging.getLogger()
    root_logger.setLevel('WARNING')
    root_logger.addHandler(logging.StreamHandler())

    parser = argparse.ArgumentParser()
    parser.add_argument("note_text", default=None, nargs="?")
    parser.add_argument("-q", "--query", help="search for notes")
    parser.add_argument("-i", "--interactive", default=False, help="edit search results in a text editor", action="store_true")
    parser.add_argument("-v", "--verbose", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--login", help="login to Evernote", action="store_true")
    parser.add_argument("--set-editor", default=None, help="set system text editor (example 'nano')")

    args = parser.parse_args()

    if args.verbose:
        root_logger.setLevel('DEBUG')

    config_store = ConfigStore()

    try:
        if args.login:
            login(config_store)
        elif args.set_editor:
            config_store.text_editor = args.set_editor
        else:
            # load auth
            try:
                auth_token = config_store.auth_token
            except ConfigLoadError:
                logger.error('Please login using "n --login"')
                return

            # load notebook
            try:
                notebook_guid = config_store.notebook_guid
            except ConfigLoadError:
                notebook_guid = None

            login_time0 = time.time()
            mn = Mininote(auth_token, notebook_guid)
            logger.debug('Login time: {}'.format(time.time() - login_time0))

            if notebook_guid is None:
                config_store.notebook_guid = mn.notebook_guid

            if args.query and args.interactive:
                try:
                    text_editor_bin = config_store.text_editor
                    edit_notes(mn, args.query, TextEditor(text_editor_bin))
                except TextEditorError:
                    logger.error('Error opening text editor\n' +
                                 'Please specify an editor with "n --set-editor <path-to-editor>"')
            elif args.query:
                query_notes(mn, args.query)
            else:
                add_note(mn, args.note_text)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
