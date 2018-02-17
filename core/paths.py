"""Resources paths."""
import os
import sys
import shutil
from argparse import ArgumentParser
from configparser import RawConfigParser


RES = os.path.join(sys.path[0], 'res')
LANGS = os.path.join(sys.path[0], 'langs')
C_WIDGETS = os.path.join(sys.path[0], 'custom_widgets')
"""custom widgets directory"""
C_RES = os.path.join(C_WIDGETS, 'res')
"""resource directory for custom widgets"""
C_LANGS = os.path.join(C_WIDGETS, 'langs')
"""langs directory for custom widgets"""

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
DEL_WIDGETS = os.path.join(RES, 'del_widgets.png')
DEL_ARCHIVES = os.path.join(RES, 'del_archives.png')

CONF_SETTINGS = os.path.join(sys.path[0], 'settings.conf')
CONF_WIDGETS = os.path.join(sys.path[0], 'widgets.conf')
CONF_PATHS = os.path.join(sys.path[0], 'paths.conf')
CONF_INSTALL = os.path.join(C_WIDGETS, 'install.conf')
STDOUT_LOG = os.path.join(sys.path[0], 'stdout.log')
STDERR_LOG = os.path.join(sys.path[0], 'stderr.log')
LICENSE_TXT = os.path.join(sys.path[0], 'license.txt')
LOCK_FILE = os.path.join(sys.path[0], '.pid.lock')

if len(sys.argv):  # parsing arguments
    parser = ArgumentParser('DeWidgets', 'DeWidgets [-c /home/alex/.dw]',
                            'Qt5 widgets for desktop.',
                            'Source code: https://github.com/InterVi/DeWidgets'
                            )
    parser.add_argument('-p', '--paths', default=None, type=str,
                        help='Load config for use custom components paths.')
    parser.add_argument('-c', '--create', default=None, type=str,
                        help='Create folders and filed into the given path.')
    result = parser.parse_known_args(sys.argv)[0]
    if result.create:
        CR = os.path.join(result.create, 'res')
        CL = os.path.join(result.create, 'langs')
        CW = os.path.join(result.create, 'custom_widgets')
        P = os.path.join(result.create, 'paths.conf')
        if not os.path.isfile(P):
            conf = RawConfigParser()
            conf['CONFIGS'] = {
                'settings': os.path.join(result.create, 'settings.conf'),
                'widgets': os.path.join(result.create, 'widgets.conf'),
                'install': os.path.join(result.create, 'install.conf')
            }
            conf['LOGS'] = {
                'stderr': os.path.join(result.create, 'stderr.log'),
                'stdout': os.path.join(result.create, 'stdout.log')
            }
            conf['OTHER'] = {
                'lock': os.path.join(result.create, '.pid.lock')
            }
            conf['DIRS'] = {
                'c_widgets': CW,
                'c_res': CR,
                'c_langs': CL
            }
            if not os.path.isdir(result.create):
                os.mkdir(result.create)
            if not os.path.isdir(CW):
                os.mkdir(CW)
            if not os.path.isdir(CR):
                os.mkdir(CR)
            if not os.path.isdir(CL):
                os.mkdir(CL)
            with open(P, 'w') as file:
                conf.write(file)
            if not os.path.isfile(os.path.join(result.create, '__init__.py')):
                shutil.copyfile(os.path.join(sys.path[0], 'custom_widgets',
                                             '__init__.py'),
                                os.path.join(CW, '__init__.py'))
        CONF_PATHS = P
    if result.paths:
        CONF_PATHS = result.paths

if os.path.isfile(CONF_PATHS):  # for user customization
    paths = RawConfigParser()
    paths.read(CONF_PATHS, 'utf-8')
    CONF_SETTINGS = paths['CONFIGS']['settings']
    CONF_WIDGETS = paths['CONFIGS']['widgets']
    CONF_INSTALL = paths['CONFIGS']['install']
    STDERR_LOG = paths['LOGS']['stderr']
    STDOUT_LOG = paths['LOGS']['stdout']
    LOCK_FILE = paths['OTHER']['lock']
    C_WIDGETS = paths['DIRS']['c_widgets']
    C_RES = paths['DIRS']['c_res']
    C_LANGS = paths['DIRS']['c_langs']


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
