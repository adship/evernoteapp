import re
from time import mktime
from datetime import datetime
from dateutil import parser


TAGREGEX = re.compile(r'#(\w+)')

class NoteParseError(Exception):
    pass

class Note:
    def __init__(self, text, updated_time = None, guid = None):
        """
        :param text: Note string
        :param updated_time: Time in epoc time
        :param guid: Note identifier
        """
        self.text = text
        self.updated_time = updated_time
        self.guid = guid

    @property
    def tags(self):
        """List of tags attached to note"""
        return TAGREGEX.findall(self.text) 

    def __str__(self):
        date = datetime.fromtimestamp(self.updated_time).strftime("%x %I:%M %p")
        return '{}: {}'.format(date, self.text)

    @staticmethod
    def parse_from_str(note_str):
        """
        Parse a string representation of a note

        :returns: Note instance
        """
        datesep = note_str.find(': ')
        if datesep == -1:
            raise NoteParseError

        try:
            updated_time = parser.parse(note_str[:datesep])
        except ValueError:
            raise NoteParseError
        text = note_str[datesep + 2:]

        return Note(text, mktime(updated_time.timetuple()))
