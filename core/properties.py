"""Provide read and write settings config."""
from os.path import isfile
from configparser import RawConfigParser
from core.paths import CONF_SETTINGS

DEFAULT = {
    'MAIN': {
        'locale': 'ru',
        'load_placed': 'False',
        'edit_mode': 'True'
    },
    'LOGS': {
        'log_level': '30',
        'stdout': '[%(levelname)s] [%(asctime)s] %(filename)s:%(lineno)d -> '
                  + '%(message)s',
        'stderr': '[%(levelname)s] [%(asctime)s] %(filename)s:%(lineno)d -> '
                  + '%(message)s',
        'cons': '[%(levelname)s] [%(asctime)s]: %(message)s'
    }
}
"""Default config dict."""


def read_settings() -> dict:
    """Read settings config.

    :return: dict
    """
    conf = RawConfigParser()
    conf.read(CONF_SETTINGS, 'utf-8')
    return dict(conf)


def write_settings(data):
    """Write dict to settings config.

    :param data: dict for write
    """
    conf = RawConfigParser()
    conf.read_dict(data)
    with open(CONF_SETTINGS, 'w', encoding='utf-8') as file:
        conf.write(file)


def is_valid(data) -> bool:
    """Check settings dict (is exists sections and keys).

    :param data: dict, settings
    :return: bool, True if settings is valid
    """
    for sec in DEFAULT:
        if sec not in data:
            return False
        if not data[sec]:
            return False
        for key in DEFAULT[sec]:
            if key not in data[sec]:
                return False
            if not data[sec][key]:
                return False
    return True


def is_exists() -> bool:
    """Check exists settings config.

    :return: bool, True if exists and correct
    """
    if isfile(CONF_SETTINGS):
        return is_valid(read_settings())
    return False


def create_default_settings():
    """Write default settings config."""
    write_settings(DEFAULT)
