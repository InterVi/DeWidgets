"""Add new widget dialog."""
import os
import sys
import json
import zipfile
from configparser import RawConfigParser
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from core.paths import ZIP, SUCCESS, ERROR, C_WIDGETS, C_RES, C_LANGS
from core.paths import CONF_INSTALL
from core.utils import STDOUT

lang = None
"""locale dict, setup from __init__"""
parent = None
"""parent QWidget, setup from __init__"""


def __init__(locale, qwparent=None):
    global lang, parent
    lang = locale
    parent = qwparent


def _get_files() -> list:
    # setup settings
    dialog = QFileDialog(parent=parent, caption=lang['ADD_NEW']['caption'],
                         filter=lang['ADD_NEW']['filter'],
                         directory=sys.path[0])
    dialog.setAcceptMode(QFileDialog.AcceptOpen)
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setWindowIcon(QIcon(ZIP))
    # setup labels
    dialog.setLabelText(QFileDialog.FileName, lang['ADD_NEW']['names'])
    dialog.setLabelText(QFileDialog.FileType, lang['ADD_NEW']['types'])
    dialog.setLabelText(QFileDialog.Accept, lang['ADD_NEW']['open'])
    dialog.setLabelText(QFileDialog.Reject, lang['ADD_NEW']['cancel'])
    # show
    dialog.show()
    if dialog.exec() == QFileDialog.Accepted:
        return dialog.selectedFiles()
    else:
        return []


def get_str_list(list_) -> str:
    result = ''
    for s in list_:
        result += s + ', '
    return result[:-2]


def _show_error(names=()):
    mbox = QMessageBox(QMessageBox.Critical, lang['ADD_NEW']['error_title'],
                       lang['ADD_NEW']['error_text'], QMessageBox.Ok, parent)
    mbox.setWindowIcon(QIcon(ERROR))
    ok = mbox.button(QMessageBox.Ok)
    ok.setText(lang['ADD_NEW']['error_ok_button'])
    ok.setToolTip(lang['ADD_NEW']['error_ok_button_tt'])
    if names:
        mbox.setInformativeText(get_str_list(names))
    mbox.exec()


def _show_success(names=()):
    mbox = QMessageBox(QMessageBox.Information,
                       lang['ADD_NEW']['success_title'],
                       lang['ADD_NEW']['success_text'], QMessageBox.Ok, parent)
    mbox.setWindowIcon(QIcon(SUCCESS))
    ok = mbox.button(QMessageBox.Ok)
    ok.setText(lang['ADD_NEW']['success_ok_button'])
    ok.setToolTip(lang['ADD_NEW']['success_ok_button_tt'])
    if names:
        mbox.setInformativeText(get_str_list(names))
    mbox.exec()


def install() -> list:
    """Init installation. Open dialog and more actions. Return list - names
    '*.py' files.
    
    Structure zip file:
    
    archive.zip\n
    - res (folder, all resources)\n
    - langs (folder, all locales)\n
    -- en.conf (ini file utf-8, example)\n
    -- ru.conf (ini file utf-8, example)\n
    - DeWidgets.txt (any file)\n
    - widget.py (python module, widget file)
    """
    files = _get_files()
    STDOUT.debug('add files: ' + str(files))
    if not files:
        return []
    broken = []  # broken files
    result = []  # widget names (*.py files)
    conf_inst = {}
    if os.path.isfile(CONF_INSTALL):
        with open(CONF_INSTALL, encoding='utf-8') as file_install:
            conf_inst = json.loads(file_install.read())
    for file in files:
        if not zipfile.is_zipfile(file):  # test
            broken.append(os.path.basename(file))
            STDOUT.debug('not zip: ' + file)
        else:
            with zipfile.ZipFile(file) as arch:
                if arch.testzip():  # test
                    broken.append(os.path.basename(file))
                    STDOUT.debug('not zip: ' + file)
                    continue
                if 'DeWidgets.txt' not in arch.namelist():  # test
                    broken.append(os.path.basename(file))
                    STDOUT.debug('not DeWidgets.txt: ' + file)
                    continue
                inst_info = {'py': [], 'res': [], 'langs': []}
                for info in arch.infolist():
                    if info.is_dir():
                        continue
                    if info.filename[-3:] == '.py':
                        # search *.py files (widgets)
                        arch.extract(info, C_WIDGETS)
                        result.append(info.filename[:-3])
                        inst_info['py'].append(os.path.join(C_WIDGETS,
                                                            info.filename))
                        STDOUT.debug('extract module: ' + info.filename)
                    elif info.filename[:3] == 'res':
                        # search files in 'res' folder
                        if not os.path.isdir(C_RES):
                            os.mkdir(C_RES)
                        r_file = os.path.join(C_RES, info.filename[4:])
                        if not os.path.isfile(r_file):
                            arch.extract(info, os.path.join(C_RES, '..'))
                            inst_info['res'].append(r_file)
                            STDOUT.debug('extract res: ' + info.filename)
                    elif info.filename[:5] == 'langs':
                        # search files in 'langs' folder
                        conf = RawConfigParser()  # lang file from patch
                        with arch.open(info) as patch:
                            conf.read_string(patch.read().decode('utf-8'))
                        if not os.path.isdir(C_LANGS):
                            os.mkdir(C_LANGS)
                        lang_file = os.path.join(C_LANGS, info.filename[6:])
                        inst_info['langs'].append((lang_file, conf._sections))
                        STDOUT.debug('process lang: ' + info.filename)
                        if os.path.isfile(lang_file):
                            # if exists - patching
                            old = RawConfigParser()  # to patch
                            old.read(lang_file)
                            for section in conf:
                                if section in old:  # patching sections
                                    for key in conf[section]:
                                        if key not in old[section]:
                                            # add new keys
                                            old[section][key] =\
                                                conf[section][key]
                                            STDOUT.debug('add key ' + key +
                                                         ' to section ' +
                                                         section)
                                else:  # adding sections
                                    old[section] = conf[section]
                                    STDOUT.debug('add section ' + section)
                            with open(lang_file, 'w',
                                      encoding='utf-8') as object_file:
                                old.write(object_file)
                            STDOUT.debug('rewrite: ' + lang_file)
                        else:  # no exists - add
                            with open(lang_file, 'w',
                                      encoding='utf-8') as object_file:
                                conf.write(object_file)
                            STDOUT.debug('create lang file: ' + lang_file)
                    conf_inst[file] = inst_info
    with open(CONF_INSTALL, 'w', encoding='utf-8') as file_install:
        file_install.write(json.dumps(conf_inst))
    if broken:  # show broken files
        _show_error(broken)
    if result:  # show widgets names (*.py files)
        _show_success(result)
    STDOUT.debug('broken: ' + str(broken))
    STDOUT.debug('result: ' + str(result))
    return result
