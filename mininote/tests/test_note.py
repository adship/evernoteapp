from datetime import datetime
from unittest import TestCase

from mininote.note import Note, NoteParseError


class TestNote(TestCase):

    def test_tag_update(self):
        """Test that hashtags are updated if text changes"""
        note = Note(text = 'foo #tag1 #tag2')
        self.assertEqual(['tag1', 'tag2'], note.tags)

        note.text = 'updated text #tag3' 
        self.assertEqual(['tag3'], note.tags)

    def test_parse_tags(self):
        """Test that hashtags are parsed from a note"""
        self.assertEqual([], Note(text = "starbucks").tags)
        self.assertEqual(["tag1"], Note(text = "cameral mocha #tag1").tags)
        self.assertEqual(["tag1", "tag2"], Note(text = "ice coffee #tag1 #tag2").tags)

    def test_str_format(self):
        """Test that note can be rendered and parsed from string"""
        notestr = str(Note('hello world', created_time = 0))

        date = datetime.fromtimestamp(0).strftime("%x %I:%M %p")
        self.assertEqual('{}: hello world'.format(date), notestr)

        note = Note.parse_from_str(notestr)
        self.assertEqual('hello world', note.text)
        self.assertEqual(0, note.created_time)

    def test_str_parse_error(self):
        """Test that exception is raised when parsing invalid note"""
        self.assertRaises(NoteParseError, lambda: Note.parse_from_str('something: invalid'))