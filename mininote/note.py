import re


TAGREGEX = re.compile(r'#(\w+)')

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
        return '<Note {}>'.format(self.text)
