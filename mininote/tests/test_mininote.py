from unittest import TestCase
from mininote.mininote import encode_note


class TestMininote(TestCase):

    def test_encode_note(self):
        """Ensure that xml characters are escaped"""
        self.assertTrue('<en-note>hello world</en-note>' in encode_note('hello world'))
        self.assertTrue('<en-note>&lt;div&gt;note&amp;"</en-note>' in encode_note('<div>note&"'))
