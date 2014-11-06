from unittest import TestCase

from mininote.note import Note


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

