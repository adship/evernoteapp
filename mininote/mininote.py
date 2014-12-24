import logging
import time
from cgi import escape
from evernote.api.client import EvernoteClient, Store
from evernote.edam.limits.constants import EDAM_NOTE_TITLE_LEN_MAX
from evernote.edam.notestore import NoteStore
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import Note as EdamNote, Notebook, NoteSortOrder
from multiprocessing.pool import ThreadPool
from xml.etree import ElementTree

from constants import EVERNOTE_NOTEBOOK, EVERNOTE_CONSUMER_KEY, EVERNOTE_MAX_PAGE_SIZE, \
                      EVERNOTE_CONSUMER_SECRET, DEVELOPMENT_MODE, EVERNOTE_FETCH_THREADS
from note import Note


logger = logging.getLogger(__name__)

def decode_note_text(note_html):
    """
    Extract note content from XML.

    :param str note_html: Note XML
    :returns: Note content
    """
    text_it = ElementTree.fromstring(note_html).itertext()

    def tostr(text):
        if type(text) == unicode:
            return text.encode('utf-8')
        else:
            return text
    return ''.join(map(lambda text: tostr(text).strip(), text_it))

def encode_note_text(text):
    """
    Return XML formatted note.

    :param str text: Note content
    :returns: XML string
    """
    template = '''<?xml version="1.0" encoding="UTF-8"?>
                  <!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
                  <en-note>{0}</en-note>'''
    return template.format(escape(text))

MAX_TITLE_LEN = EDAM_NOTE_TITLE_LEN_MAX - 2
CONTENT_FETCH_THRESHOLD = len(encode_note_text('')) + MAX_TITLE_LEN

class Mininote(object):
    """Provides access to the Evernote 'database'."""

    def __init__(self, token, notebook_guid=None):
        """
        :param str token: The Evernote auth token
        :param str notebook_guid: The Evernote notebook GUID or None if not known
        """
        client = EvernoteClient(token=token,
                                consumer_key=EVERNOTE_CONSUMER_KEY,
                                consumer_secret=EVERNOTE_CONSUMER_SECRET,
                                sandbox=DEVELOPMENT_MODE)
        self._token = token
        self._note_store_uri = client.get_user_store().getNoteStoreUrl()
        self._thread_pool = ThreadPool(processes=EVERNOTE_FETCH_THREADS)

        self.notebook_guid = notebook_guid or self._get_create_notebook()

    def _note_store(self):
        """
        :returns: new NoteStore instance
        """
        return Store(self._token, NoteStore.Client, self._note_store_uri)

    def add_note(self, note):
        """
        :param Note note: The mininote Note instance
        """
        logger.debug('add note: {}'.format(note.text))
        self._note_store().createNote(convert_to_enote(note, self.notebook_guid))

    def search(self, string):
        """
        :param str string: The Evernote search query string
        :returns: An iterator to retrieve notes
        """
        def get_page(start):
            result_spec = NotesMetadataResultSpec(includeTitle=True,
                                                  includeCreated=True,
                                                  includeUpdated=True,
                                                  includeContentLength=True)
            return self._note_store().findNotesMetadata(note_filter,
                                                        start,
                                                        EVERNOTE_MAX_PAGE_SIZE,
                                                        result_spec)

        def iter_note_metadata(note_filter):
            i = 0
            while True:
                time0 = time.time()
                page = get_page(i)
                logger.debug('Page fetch time: {}'.format(time.time() - time0))
                for note_metadata in page.notes:
                    yield note_metadata
                i += len(page.notes)
                if i >= page.totalNotes:
                    break

        def fetch_note(note_metadata):
            if note_metadata.contentLength > CONTENT_FETCH_THRESHOLD:
                note = self._note_store().getNote(note_metadata.guid, True, False, False, False)
            else:
                note = None
            return convert_to_mininote(note_metadata, note)

        note_filter = NoteFilter(words=string,
                                 ascending=True,
                                 order=NoteSortOrder.UPDATED,
                                 notebookGuid=self.notebook_guid)
        return self._thread_pool.imap(fetch_note, iter_note_metadata(note_filter))

    def update_note(self, note):
        """
        :param Note note: The mininote Note instance
        """
        logger.debug('update_note: {}'.format(note))
        self._note_store().updateNote(convert_to_enote(note, self.notebook_guid))

    def delete_note(self, note):
        """
        :param Note note: The mininote Note instance
        """
        logger.debug('delete note: {}'.format(note))
        self._note_store().deleteNote(note.guid)

    def _get_create_notebook(self):
        """
        Get or create the Evernote notebook.

        :returns: Notebook guid
        """
        for notebook in self._note_store().listNotebooks():
            if notebook.name == EVERNOTE_NOTEBOOK:
                return notebook.guid
        return self._note_store() \
                   .createNotebook(Notebook(name=EVERNOTE_NOTEBOOK)) \
                   .guid

def convert_to_mininote(note_metadata, note):
    """
    Convert Evernote note to Mininote note
    :param NoteMetadata note_metadata: note metadata
    :param Note note: full note or None if not available
    """
    if note:
        content = decode_note_text(note.content)
    else:
        if (len(note_metadata.title) >= 2 and
           note_metadata.title.startswith('"') and
           note_metadata.title.endswith('"')):
                content = note_metadata.title[1: -1]
        else:
            content = note_metadata.title

    return Note(text=content,
                updated_time=note_metadata.updated / 1000,
                created_time=note_metadata.created / 1000,
                guid=note_metadata.guid)

def convert_to_enote(note, notebook_guid=None):
    """
    Convert Mininote note to Evernote note
    :param note: The mininote Note instance
    """
    created = note.created_time * 1000 if note.created_time else None
    return EdamNote(guid=note.guid,
                    notebookGuid=notebook_guid,
                    title='"{}"'.format(note.text[0: MAX_TITLE_LEN]),
                    content=encode_note_text(note.text),
                    updated=None,
                    created=created,
                    tagNames=note.tags)
