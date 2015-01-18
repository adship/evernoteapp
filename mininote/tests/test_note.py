# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import TestCase

from mininote.note import Note, NoteParseError


class TestNote(TestCase):

    def test_tag_update(self):
        """Test that hashtags are updated if text changes"""
        note = Note(text='foo #tag1 #tag2')
        self.assertEqual({'tag1', 'tag2'}, note.tags)

        note.text = 'updated text #tag3'
        self.assertEqual({'tag3'}, note.tags)

    def test_parse_tags(self):
        """Test that hashtags are parsed from a note"""
        self.assertEqual(set(), Note(text="starbucks").tags)
        self.assertEqual(set(), Note(text="http://google.com#foo has no tags").tags)
        self.assertEqual({"tag1", "tag2"}, Note(text="ice coffee #tag1 #tag2").tags)
        self.assertEqual({"dup"}, Note(text="note with #dup #dup").tags)
        self.assertEqual({"normalized"}, Note(text="note with #normalized #Normalized").tags)
        self.assertEqual({"has-dash"}, Note(text="note with #has-dash").tags)
        self.assertEqual({"has_uscore"}, Note(text="note with #has_uscore").tags)

        self.assertEqual({u"ß".encode("utf-8"), u"öo".encode("utf-8")}, Note(text=u"#ß #öo".encode('utf-8')).tags)
        self.assertEqual({"start", "end"}, Note(text="#start #end").tags)
        self.assertEqual({"tab"}, Note(text="\t#tab").tags)
        self.assertEqual({"sub"}, Note(text="#sub#tag?").tags)
        self.assertEqual({"coffee"}, Note(text="#coffee: caramel mocha").tags)
        self.assertEqual({"coffee"}, Note(text="#coffee- caramel mocha").tags)
        self.assertEqual(set(), Note(text="#: #.").tags)
        self.assertEqual({"-b", "w"}, Note(text="single char tags #-b #w-").tags)

    def test_str_format(self):
        """Test that note can be rendered and parsed from string"""
        notestr = str(Note('hello world', created_time=0))

        date = datetime.fromtimestamp(0).strftime("%x %I:%M %p")
        self.assertEqual('{}: hello world'.format(date), notestr)

        note = Note.parse_from_str(notestr)
        self.assertEqual('hello world', note.text)
        self.assertEqual(0, note.created_time)

    def test_str_parse_error(self):
        """Test that exception is raised when parsing invalid note"""
        self.assertRaises(NoteParseError, lambda: Note.parse_from_str('something: invalid'))
