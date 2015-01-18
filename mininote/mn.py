#!/usr/bin/env python
import logging
import time
from colorstr import colorstr
from note import Note, NoteParseError


logger = logging.getLogger(__name__)

def login(mn, config_store, args):
    """
    Run through oauth procedure and store authentication token.

    :param Mininote mn: Mininote instance
    :param ConfigStore config_store: User configuration
    :param argparse.Namespace args: Command line options
    """
    from oauth import get_auth_token, OAuthError

    config_store.delete_auth()
    try:
        config_store.auth_token = get_auth_token()
    except OAuthError as e:
        logger.error(e.message)

def add_note(mn, config_store, args):
    """
    Save a new note.

    :param Mininote mn: Mininote instance
    :param ConfigStore config_store: User configuration
    :param argparse.Namespace args: Command line options
    """
    if args.note is None:
        note_string = raw_input(colorstr('DIM', 'mn> '))
    else:
        note_string = args.note
    mn.add_note(Note(note_string))

def query_notes(mn, config_store, args):
    """
    Display search results.

    :param Mininote mn: Mininote instance
    :param ConfigStore config_store: User configuration
    :param argparse.Namespace args: Command line options
    """
    from collections import Counter

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
    for note in mn.search(args.note):
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

def edit_notes(mn, config_store, args):
    """
    Display search results and allow edits.

    :param Mininote mn: Mininote instance
    :param ConfigStore config_store: User configuration
    :param argparse.Namespace args: Command line options
    """
    from match_notes import match_notes

    text_editor = args.text_editor
    before_notes = list(mn.search(args.note))
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

def set_editor(mn, config_store, args):
    """
    Set desired text editor.

    :param Mininote mn: Mininote instance
    :param ConfigStore config_store: User configuration
    :param argparse.Namespace args: Command line options
    """
    config_store.text_editor = args.text_editor

def main():
    import sys
    import argparse
    import colorama
    from config_store import ConfigStore, ConfigLoadError
    from mininote import Mininote
    from texteditor import TextEditor, TextEditorError

    class NotLoggedInError(Exception):
        """Error for user not logged in."""

    def get_mn(config_store):
        """
        :param ConfigStore config_store: User configuration
        :returns: Mininote instance
        """
        try:
            auth_token = config_store.auth_token
        except ConfigLoadError:
            raise NotLoggedInError()

        try:
            notebook_guid = config_store.notebook_guid
        except ConfigLoadError:
            notebook_guid = None

        login_time0 = time.time()
        mn = Mininote(auth_token, notebook_guid)
        logger.debug('Login time: {}'.format(time.time() - login_time0))
        return mn

    colorama.init()

    root_logger = logging.getLogger()
    root_logger.setLevel('WARNING')
    root_logger.addHandler(logging.StreamHandler())

    config_store = ConfigStore()
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help=argparse.SUPPRESS)

    if len(sys.argv) > 1:
        subparsers = parser.add_subparsers()

        addnote = subparsers.add_parser('add')
        addnote.add_argument('note', help='Note text')
        addnote.set_defaults(handler=add_note, authorized=True)

        searchnote = subparsers.add_parser('search')
        searchnote.add_argument('note', help='Note search filter')
        searchnote.set_defaults(handler=query_notes, authorized=True)

        loginopt = subparsers.add_parser('login')
        loginopt.set_defaults(handler=login, authorized=False)

        editnote = subparsers.add_parser('edit')
        editnote.add_argument('note', help='Note search filter')
        editnote.set_defaults(handler=edit_notes, authorized=True, text_editor=TextEditor(config_store.text_editor))

        editor = subparsers.add_parser('set-editor')
        editor.add_argument('text_editor', help='Name of text editor')
        editor.set_defaults(handler=set_editor, authorized=False)
    else:
        # default is add note
        parser.set_defaults(handler=add_note, authorized=True, note=None)

    args = parser.parse_args()

    if args.verbose:
        root_logger.setLevel('DEBUG')

    try:
        mn = get_mn(config_store) if args.authorized else None
        args.handler(mn, config_store, args)
    except NotLoggedInError:
        logger.error('Please login using "mn --login"')
    except TextEditorError:
        logger.error('Error opening text editor\n' +
                     'Please specify an editor with \'mn set-editor "<path-to-editor>"\'')
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
