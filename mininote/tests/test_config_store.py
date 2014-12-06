import json
from mock import Mock, mock_open, patch
from StringIO import StringIO
from unittest import TestCase

from mininote.config_store import ConfigStore, ConfigLoadError


class TestConfigStore(TestCase):
    """Tests for configuration store"""

    def patch_open(self, data):
        self.mock_open = mock_open(read_data=data)
        return patch("mininote.config_store.open", self.mock_open, create=True)

    def get_written_data(self):
        writes = self.mock_open().write.call_args_list
        return ''.join([w[0][0] for w in writes])

    def test_read_cfg_token(self):
        """Token is read from config if present"""
        data = json.dumps({'auth_token' : 'foo'})
        with self.patch_open(data):
            cfg = ConfigStore()
            self.assertEqual('foo', cfg.auth_token)

    def test_read_text_editor(self):
        """Text editor is read from config if present"""
        data = json.dumps({'text_editor' : 'foo'})
        with self.patch_open(data):
            cfg = ConfigStore()
            self.assertEqual('foo', cfg.text_editor)

    @patch('mininote.config_store.get_sys_text_editor', return_value='vim')
    def test_read_default_text_editor(self, DefaultEditor):
        """Default editor is returned if config not present"""
        data = json.dumps({})
        with self.patch_open(data):
            cfg = ConfigStore()
            self.assertEqual('vim', cfg.text_editor)

    def test_read_cfg_notfound(self):
        """Test that has expected exception if config not present"""
        data = json.dumps({})
        with self.patch_open(data):
            cfg = ConfigStore()
            self.assertRaises(ConfigLoadError, lambda: cfg.auth_token)

    def test_read_cfg_invalid_file(self):
        """Test that has expected exception if file is invalid"""
        data = 'notvalidjson'
        with self.patch_open(data):
            cfg = ConfigStore()
            self.assertRaises(ConfigLoadError, lambda: cfg.auth_token)

    def test_read_cfg_missing_file(self):
        """Test that has expected exception if file is missing"""
        mock = Mock()
        mock.side_effect = IOError
        with patch("mininote.config_store.open", mock, create=True):
            cfg = ConfigStore()
            self.assertRaises(ConfigLoadError, lambda: cfg.auth_token)

    def test_write_content(self):
        """Test that expected content is written to file"""
        data = json.dumps({'key1':'val1'})
        with self.patch_open(data):
            cfg = ConfigStore()
            cfg.auth_token = 'foo'

        expected_write = {'auth_token': 'foo', 'key1': 'val1'} 
        self.assertEqual(expected_write, json.loads(self.get_written_data()))
