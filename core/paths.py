"""Resources paths."""
import os
import sys


RES = os.path.join(sys.path[0], 'res')
LANGS = os.path.join(sys.path[0], 'langs')

AVA = os.path.join(RES, 'ava.jpg')
DELETE = os.path.join(RES, 'delete.png')
DeWidgetsIcon = os.path.join(RES, 'DeWidgetsIcon.png')
ERROR = os.path.join(RES, 'error.png')
HELP = os.path.join(RES, 'help.png')
LICENSE = os.path.join(RES, 'license.png')
SUCCESS = os.path.join(RES, 'success.png')
ZIP = os.path.join(RES, 'zip.png')
MOVE = os.path.join(RES, 'move.png')
SETTINGS = os.path.join(RES, 'settings.png')
WIDGET = os.path.join(RES, 'widget.png')
SHOW = os.path.join(RES, 'show.png')
HIDE = os.path.join(RES, 'hide.png')
EXIT = os.path.join(RES, 'exit.png')
LOAD = os.path.join(RES, 'load.png')
UNLOAD = os.path.join(RES, 'unload.png')
RELOAD = os.path.join(RES, 'reload.png')
PLAY = os.path.join(RES, 'play.png')
PAUSE = os.path.join(RES, 'pause.png')
STOP = os.path.join(RES, 'stop.png')

CONF_SETTINGS = os.path.join(sys.path[0], 'settings.conf')
CONF_WIDGETS = os.path.join(sys.path[0], 'widgets.conf')
STDOUT_LOG = os.path.join(sys.path[0], 'stdout.log')
STDERR_LOG = os.path.join(sys.path[0], 'stderr.log')
LICENSE_TXT = os.path.join(sys.path[0], 'license.txt')
LOCK_FILE = os.path.join(sys.path[0], '.lock.lck')


def get_paths(folder=RES, files=True) -> dict:
    """Get file or subdir paths in given dir.
    
    :param folder: full path to dir
    :param files: True - only files, False - only dirs
    :return: dict, keys - file or dir names (without extensions ([name].ext)),
    values - full paths
    """
    result = {}
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if files and not os.path.isfile(path):
            continue
        elif not files and not os.path.isdir(path):
            continue
        result[name[:name.rfind('.')]] = path
    return result
