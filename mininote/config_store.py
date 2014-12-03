import json
import os
import platform


class ConfigLoadError(Exception):
    """Unable to read configuration"""

class ConfigStore(object):
    """Access to configuration and default settings"""
    AUTH_TOKEN = 'auth_token'

    @property
    def auth_token(self):
        """User authentication token"""
        return read_config_key(self.AUTH_TOKEN)

    @auth_token.setter
    def auth_token(self, token):
        write_config_key(self.AUTH_TOKEN, token)

def get_cfg_loc():
    """
    :returns: Path to configuration file
    """
    windows = "Windows" in platform.system()
    my_environ = os.environ.copy()

    if windows:
        path = os.path.join(my_environ["USERPROFILE"], "AppData", "Roaming", "mininote")
    else:
        path = os.path.join(my_environ["HOME"], ".mininote")
    return path


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
    with open(get_cfg_loc(), 'w') as fp:
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
        with open(get_cfg_loc()) as fp:
            return json.load(fp)
    except (ValueError, IOError):
        return {}
