from unittest import TestCase
from mininote.mininote import get_tags

class TestMininote(TestCase):

    def test_parse_tags(self):
        self.assertEqual([], get_tags("starbucks"))
        self.assertEqual(["tag1"], get_tags("cameral mocha #tag1"))
        self.assertEqual(["tag1", "tag2"], get_tags("ice coffee #tag1 #tag2"))





        

        

    
