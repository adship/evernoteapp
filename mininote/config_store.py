import json
import os
import platform
from constants import DEFAULT_EDITOR_OTHER, DEFAULT_EDITOR_WIN


class ConfigLoadError(Exception):
    """Unable to read configuration"""

class ConfigStore(object):
    """Access to configuration and default settings"""
    AUTH_TOKEN = 'auth_token'
    TEXT_EDITOR = 'text_editor'
    NOTEBOOK_GUID = 'notebook_guid'

    def delete_auth(self):
        """Remove data associated with user account."""
        config = self._read_config()
        for key in [self.AUTH_TOKEN, self.NOTEBOOK_GUID]:
            if key in config:
                config.pop(key)
        self._write_config(config)

    @property
    def notebook_guid(self):
        """
        :returns: Evernote notebook GUID
        :raises: ConfigLoadError if not present
        """
        return self._read_config_key(self.NOTEBOOK_GUID)

    @notebook_guid.setter
    def notebook_guid(self, guid):
        """
        :param str guid: The Evernote notebook GUID
        """
        self._write_config_key(self.NOTEBOOK_GUID, guid)

    @property
    def auth_token(self):
        """
        :returns: User authentication token
        :raises: ConfigLoadError if not present
        """
        return self._read_config_key(self.AUTH_TOKEN)

    @auth_token.setter
    def auth_token(self, token):
        """
        :param str token: the authentication token
        """
        self._write_config_key(self.AUTH_TOKEN, token)

    @property
    def text_editor(self):
        """
        :returns: Path to text editor binary
        """
        try:
            return self._read_config_key(self.TEXT_EDITOR)
        except ConfigLoadError:
            return self._get_sys_text_editor()

    @text_editor.setter
    def text_editor(self, text_editor):
        """
        :param text_editor: Path to text editor binary
        """
        self._write_config_key(self.TEXT_EDITOR, text_editor)

    def _write_config(self, config):
        """
        Write entire contents of config file.

        :param dict config: Config to write
        """
        with open(self._get_sys_cfg_loc(), 'w') as fp:
            json.dump(config, fp, indent=4)

    def _write_config_key(self, key, value):
        """
        Write single value to store.

        :param str key: Name of key
        :param str value: Value for key
        """
        try:
            config = self._read_config()
        except ConfigLoadError:
            config = {}

        config[key] = value
        self._write_config(config)

    def _read_config_key(self, key):
        """
        Read single value from store.

        :param str key: Name of key
        :returns: Configuration value for key
        :raises: ConfigLoadError if config cannot be loaded
        """
        try:
            return self._read_config()[key]
        except KeyError:
            raise ConfigLoadError

    def _read_config(self):
        """
        Read entire contents of config file.

        :returns: Dict
        """
        try:
            with open(self._get_sys_cfg_loc()) as fp:
                return json.load(fp)
        except (ValueError, IOError):
            return {}

    @staticmethod
    def _get_sys_cfg_loc():
        """
        :returns: Path to configuration file
        """
        my_environ = os.environ.copy()

        if 'Windows' in platform.system():
            path = os.path.join(my_environ['USERPROFILE'], 'AppData', 'Roaming', 'mininote')
        else:
            path = os.path.join(my_environ['HOME'], '.mininote')
        return path

    @staticmethod
    def _get_sys_text_editor():
        """
        Guess which text editor to use.

        :returns: Default text editor binary for system
        """
        if 'Windows' in platform.system():
            return DEFAULT_EDITOR_WIN
        else:
            return os.environ.get('EDITOR', DEFAULT_EDITOR_OTHER)
