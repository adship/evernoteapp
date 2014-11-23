import re
from time import mktime
from datetime import datetime
from dateutil import parser


TAGREGEX = re.compile(r'#(\w+)')

class NoteParseError(Exception):
    pass

class Note:
    def __init__(self, text, **kwargs):
        """
        :param text: Note string
        :param guid: Evernote note identifier
        :param created_time: Time in epoc time
        :param updated_time: Time in epoc time
        """
        self.text = text
        self.guid = kwargs.get('guid')
        self.created_time = kwargs.get('created_time')
        self.updated_time = kwargs.get('updated_time')

    @property
    def tags(self):
        """List of tags attached to note"""
        return TAGREGEX.findall(self.text) 

    def __str__(self):
        created = datetime.fromtimestamp(self.created_time).strftime("%x %I:%M %p")
        return '{}: {}'.format(created, self.text)

    @staticmethod
    def parse_from_str(note_str):
        """
        Parse a string representation of a note

        :returns: Note instance
        :raises: NoteParseError
        """
        datesep = note_str.find(': ')
        if datesep == -1:
            raise NoteParseError

        try:
            updated_time = parser.parse(note_str[:datesep])
        except (TypeError, TypeError):
            raise NoteParseError
        text = note_str[datesep + 2:]

        return Note(text, created_time = mktime(updated_time.timetuple()))
