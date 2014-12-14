from mock import Mock, mock_open, patch
from unittest import TestCase

from mininote.config_store import ConfigStore, ConfigLoadError


class MockConfigStore(ConfigStore):
    """Fake out ConfigStore file access."""

    def __init__(self, config):
        """
        :param dict config: Fake data
        """
        self.config = config

    def _read_config(self):
        return self.config

    def _write_config(self, config):
        self.config = config

    @staticmethod
    def _get_sys_text_editor():
        return 'vim'

class TestConfigStoreReadWrite(TestCase):
    """Read write tests for ConfigStore"""

    def test_read_cfg(self):
        """Config is read from file correctly"""
        cfg = {'auth_token': 'token',
               'text_editor': 'vim',
               'notebook_guid': 'guid'}
        store = MockConfigStore(cfg)
        self.assertEqual('token', store.auth_token)
        self.assertEqual('vim', store.text_editor)
        self.assertEqual('guid', store.notebook_guid)

    def test_read_cfg_defaults(self):
        """Behavior is correct if config not present"""
        store = MockConfigStore(config={})
        self.assertEqual('vim', store.text_editor)
        self.assertRaises(ConfigLoadError, lambda: store.auth_token)
        self.assertRaises(ConfigLoadError, lambda: store.notebook_guid)

    def test_write_cfg(self):
        """Config is written to file correctly"""
        store = MockConfigStore(config={})
        store.auth_token = 'token'
        store.text_editor = 'vim'
        store.notebook_guid = 'guid'

        cfg = {'auth_token': 'token',
               'text_editor': 'vim',
               'notebook_guid': 'guid'}
        self.assertEqual(cfg, store.config)

    def test_delete_auth(self):
        """Test that user account data is removed"""
        cfg = {'auth_token': 'token',
               'text_editor': 'vim',
               'notebook_guid': 'guid'}
        store = MockConfigStore(cfg)
        store.delete_auth()

        cfg = {'text_editor': 'vim'}
        self.assertEqual(cfg, store.config)

class TestConfigStoreFileIO(TestCase):
    """File IO tests for ConfigStore"""

    def patch_open(self, data):
        self.mock_open = mock_open(read_data=data)
        return patch("mininote.config_store.open", self.mock_open, create=True)

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
