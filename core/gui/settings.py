"""Edit gui settings app."""
import os
import sys
import traceback
from configparser import ConfigParser
from PyQt5.QtWidgets import QWidget, QPushButton, QCheckBox, QComboBox, QLabel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QRect
from core.gui.del_widgets import Delete
from core.paths import SETTINGS, SUCCESS, LANGS, CONF_SETTINGS


class Settings(QWidget):
    """settings window"""
    def __init__(self, lang, main, settings):
        """

        :param lang: dict, current locale
        :param main: core.gui.gui.Main class
        :param settings: dict, current settings
        """
        super().__init__()
        self.lang = lang
        self.main = main
        self.settings = settings
        self._items = {}
        # setup window
        self.setWindowTitle(lang['SETTINGS']['title'])
        self.setWindowIcon(QIcon(SETTINGS))
        self.setFixedSize(286, 171)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |
                            Qt.WindowCloseButtonHint)
        # setup languages list
        self.language = QComboBox(self)
        self.language.setGeometry(QRect(20, 30, 246, 23))
        self.language.setToolTip(lang['SETTINGS']['language_tt'])
        self.language.activated.connect(self._item_select)
        self._box_fill()
        # setup 'Load placed' checkbox
        self.load_placed = QCheckBox(self)
        self.load_placed.setGeometry(QRect(2, 70, 282, 20))
        self.load_placed.setText(lang['SETTINGS']['load_placed'])
        self.load_placed.setToolTip(lang['SETTINGS']['load_placed_tt'])
        if settings['MAIN']['load_placed'].lower() in ('true', 'yes', 'on'):
            self.load_placed.setChecked(True)
        # setup 'Languages' lebel
        self.label = QLabel(self)
        self.label.setGeometry(QRect(70, 10, 151, 16))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setText(lang['SETTINGS']['label'])
        # setup widgets delete button
        self.del_button = QPushButton(lang['SETTINGS']['del_button'], self)
        self.del_button.setToolTip(lang['SETTINGS']['del_button_tt'])
        self.del_button.setGeometry(QRect(80, 100, 125, 27))
        self.del_button.clicked.connect(self._show_del_widgets)
        # setup 'Save' button
        self.save_button = QPushButton(lang['SETTINGS']['save_button'], self)
        self.save_button.setToolTip(lang['SETTINGS']['save_button_tt'])
        self.save_button.setGeometry(QRect(2, 140, 94, 27))
        self.save_button.clicked.connect(self._save)
        # setup 'Cancel' button
        self.cancel_button = QPushButton(lang['SETTINGS']['cancel_button'],
                                         self)
        self.cancel_button.setToolTip(lang['SETTINGS']['cancel_button_tt'])
        self.cancel_button.setGeometry(QRect(190, 140, 94, 27))
        self.cancel_button.clicked.connect(self._cancel)
        # show
        self.show()

    def _box_fill(self):
        for name in os.listdir(LANGS):
            try:
                file = os.path.join(LANGS, name)
                conf = ConfigParser()
                conf.read(file)
                # checks
                if 'LANG' not in conf:
                    continue
                cont = False
                for key in ('name', 'description', 'language', 'country'):
                    if key not in conf['LANG']:
                        cont = True
                        break
                if cont:
                    continue
                # fill
                item = conf['LANG']['name'] + ' ('
                item += conf['LANG']['description'] + ')'
                self.language.addItem(item)
                if name[:-5] == self.settings['MAIN']['locale']:
                    self.language.setCurrentText(item)
                self._items[item] = name[:-5]
            except:
                print(traceback.format_exc())

    def _item_select(self):
        try:
            # item = self._items[self.language.currentText()]
            pass
        except:
            print(traceback.format_exc())

    def _save(self):
        try:
            self.settings['MAIN']['locale'] =\
                self._items[self.language.currentText()]
            self.settings['MAIN']['load_placed'] =\
                str(self.load_placed.isChecked())
            with open(CONF_SETTINGS, 'w') as file:
                self.settings.write(file)
            self._show_warn()
            self.main._list_fill()
            # strange bug: open from tray (main win hide),
            # call self.close() -> exit app
            self.destroy()
        except:
            print(traceback.format_exc())

    def _cancel(self):
        try:
            self.main._list_fill()
            self.destroy()
        except:
            print(traceback.format_exc())

    def _show_warn(self):
        mbox = QMessageBox(self)
        mbox.setWindowIcon(QIcon(SUCCESS))
        mbox.setIcon(QMessageBox.Warning)
        mbox.setWindowTitle(self.lang['SETTINGS']['warn_title'])
        mbox.setText(self.lang['SETTINGS']['warn_text'])
        mbox.setStandardButtons(QMessageBox.Ok)
        ok = mbox.button(QMessageBox.Ok)
        ok.setText(self.lang['SETTINGS']['warn_ok_button'])
        ok.setToolTip(self.lang['SETTINGS']['warn_ok_button_tt'])
        mbox.exec()

    def _show_del_widgets(self):
        try:
            self.del_widgets_win = Delete(self.lang,
                                          sys.modules['core.gui.gui'].manager)
        except:
            print(traceback.format_exc())
