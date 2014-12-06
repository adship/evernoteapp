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

    @property
    def auth_token(self):
        """
        :returns: User authentication token
        """
        return read_config_key(self.AUTH_TOKEN)

    @auth_token.setter
    def auth_token(self, token):
        """
        :param str token: the authentication token
        :raises: ConfigLoadError
        """
        write_config_key(self.AUTH_TOKEN, token)

    @property
    def text_editor(self):
        """
        :returns: Path to text editor binary
        """
        try:
            return read_config_key(self.TEXT_EDITOR)
        except ConfigLoadError:
            return get_sys_text_editor()

    @text_editor.setter
    def text_editor(self, text_editor):
        """
        :param text_editor: Path to text editor binary
        """
        write_config_key(self.TEXT_EDITOR, text_editor)


def get_sys_cfg_loc():
    """
    :returns: Path to configuration file
    """
    my_environ = os.environ.copy()

    if 'Windows' in platform.system():
        path = os.path.join(my_environ['USERPROFILE'], 'AppData', 'Roaming', 'mininote')
    else:
        path = os.path.join(my_environ['HOME'], '.mininote')
    return path

def get_sys_text_editor():
    """
    Guess which text editor to use.

    :returns: Default text editor binary for system
    """
    if 'Windows' in platform.system():
        return DEFAULT_EDITOR_WIN
    else:
        return os.environ.get('EDITOR', DEFAULT_EDITOR_OTHER)

def write_config_key(key, value):
    """
    Write value to store.

    :param str key: Name of key
    :param str value: Value for key
    """
    try:
        config = read_config()
    except ConfigLoadError:
        config = {}

    config[key] = value
    with open(get_sys_cfg_loc(), 'w') as fp:
        json.dump(config, fp, indent=4)

def read_config_key(key):
    """
    Read value from store.

    :param str key: Name of key
    :returns: Configuration value for key
    :raises: ConfigLoadError if config cannot be loaded
    """
    try:
        return read_config()[key]
    except KeyError:
        raise ConfigLoadError

def read_config():
    """
    Read entire contents of config file

    :returns: Dict
    """
    try:
        with open(get_sys_cfg_loc()) as fp:
            return json.load(fp)
    except (ValueError, IOError):
        return {}

