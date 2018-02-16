"""Manage locales - get list and conf."""
from configparser import RawConfigParser
from core.paths import LANGS, C_LANGS, get_paths


def __validate(path) -> bool:
    conf = RawConfigParser()
    conf.read(path, 'utf-8')
    if 'LANG' not in conf:
        return False
    for key in ('name', 'description', 'language', 'country'):
        if key not in conf['LANG']:
            return False
    return True


def __get_locales(path) -> list:
    result = []
    files = get_paths(path)
    for name in files:
        if __validate(files[name]):
            result.append(name)
    return result


def get_locales() -> list:
    """Get correct locale names.

    :return: list
    """
    return __get_locales(LANGS)


def get_locale(name) -> dict:
    """Get locale.

    :param name: str, locale name (file name without ext).
    :return: dict
    """
    conf = RawConfigParser()
    conf.read(get_paths(LANGS)[name], 'utf-8')
    return dict(conf)


def get_custom_locales() -> list:
    """Get correct custom locale names (for user widgets).

    :return: list
    """
    return __get_locales(C_LANGS)


def get_custom_locale(name) -> dict:
    """Get custom locale (for user widgets).

    :param name: str, locale name (file name without ext).
    :return: dict
    """
    conf = RawConfigParser()
    conf.read(get_paths(C_LANGS)[name], 'utf-8')
    return dict(conf)


def is_exists(name) -> bool:
    """Check exists locale.

    :param name: str, locale name (file name without ext).
    :return: bool, True if exists
    """
    files = get_paths(LANGS)
    if name in files:
        return __validate(files[name])
    return False


def custom_is_exists(name) -> bool:
    """Check exists custom locale (for user widgets).

    :param name: str, locale name (file name without ext).
    :return: bool, True if exists
    """
    files = get_paths(C_LANGS)
    if name in files:
        return __validate(files[name])
    return False
