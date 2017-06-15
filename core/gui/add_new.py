"""Add new widget dialog."""
import os
import sys
import zipfile
from configparser import ConfigParser
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from core.paths import ZIP, SUCCESS, ERROR, CONF_WIDGETS, RES

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
    dialog.exec()
    return dialog.selectedFiles()


def get_str_list(list_) -> str:
    result = ''
    for s in list_:
        result += s + ', '
    return result[:-2]


def _show_error(names=()):
    mbox = QMessageBox(parent)
    mbox.setIcon(QMessageBox.Critical)
    mbox.setWindowIcon(QIcon(ERROR))
    mbox.setWindowTitle(lang['ADD_NEW']['error_title'])
    mbox.setText(lang['ADD_NEW']['error_text'])
    mbox.setStandardButtons(QMessageBox.Ok)
    ok = mbox.button(QMessageBox.Ok)
    ok.setText(lang['ADD_NEW']['error_ok_button'])
    ok.setToolTip(lang['ADD_NEW']['error_ok_button_tt'])
    if names:
        mbox.setInformativeText(get_str_list(names))
    mbox.exec()


def _show_success(names=()):
    mbox = QMessageBox(parent)
    mbox.setWindowIcon(QIcon(SUCCESS))
    mbox.setIcon(QMessageBox.Information)
    mbox.setWindowTitle(lang['ADD_NEW']['success_title'])
    mbox.setText(lang['ADD_NEW']['success_text'])
    mbox.setStandardButtons(QMessageBox.Ok)
    ok = mbox.button(QMessageBox.Ok)
    ok.setText(lang['ADD_NEW']['success_ok_button'])
    ok.setToolTip(lang['ADD_NEW']['success_ok_button_tt'])
    if names:
        mbox.setInformativeText(get_str_list(names))
    mbox.exec()


def install() -> list:
    """Init installation. Open dialog and more actions.
    
    Structure zip file:
    
    archive.zip\n
    - res (folder, all resources)\n
    - langs (folder, all locales)\n
    -- en.conf (ini file utf-8, example)\n
    -- ru.conf (ini file utf-8, example)\n
    - DeWidgets (file or folder, say 'I widget for DeWidget!')\n
    - widget.py (python module, widget file)
    """
    files = _get_files()
    broken = []  # broken files
    result = []  # widget names (*.py files)
    for file in files:
        if not zipfile.is_zipfile(file):  # test
            broken.append(os.path.basename(file))
        else:
            with zipfile.ZipFile(file) as arch:
                if arch.testzip():  # test
                    broken.append(os.path.basename(file))
                    continue
                if 'DeWidgets' not in arch.namelist():  # test
                    broken.append(os.path.basename(file))
                    continue
                for info in arch.infolist():
                    if info.is_dir():
                        continue
                    if info.filename[-3:] == '.py':
                        # search *.py files (widgets)
                        arch.extract(info, CONF_WIDGETS)
                        result.append(info.filename[:-3])
                    elif info.filename[:3] == 'res':
                        # search files in 'res' folder
                        if not os.path.isfile(os.path.join(RES,
                                                           info.filename[4:])):
                            arch.extract(info, sys.path[0])
                    elif info.filename[:5] == 'langs':
                        # search files in 'langs' folder
                        conf = ConfigParser()  # lang file from patch
                        with arch.open(info) as patch:
                            conf.read_string(patch.read().decode('utf-8'))
                        lang_file = os.path.join(sys.path[0], 'langs',  # to
                                                 info.filename[6:])
                        if os.path.isfile(lang_file):
                            # if exists - patching
                            old = ConfigParser()  # to patch
                            old.read(lang_file)
                            for section in conf:
                                if section in old:  # patching sections
                                    for key in conf[section]:
                                        if key not in old[section]:
                                            # add new keys
                                            old[section][key] =\
                                                conf[section][key]
                                else:  # adding sections
                                    old[section] = conf[section]
                            with open(lang_file, 'w') as object_file:
                                old.write(object_file)
                        else:  # no exists - add
                            with open(lang_file, 'w') as object_file:
                                conf.write(object_file)
    if broken:  # show broken files
        _show_error(broken)
    if result:  # show widgets names (*.py files)
        _show_success(result)
    return result
