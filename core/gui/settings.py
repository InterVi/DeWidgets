"""Edit gui settings app."""
import os
import sys
import traceback
from configparser import ConfigParser
from PyQt5.QtWidgets import QWidget, QPushButton, QCheckBox, QComboBox, QLabel
from PyQt5.QtWidgets import QMessageBox, QGridLayout, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
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
        self.resize(290, 175)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |
                            Qt.WindowCloseButtonHint)
        # setup languages list
        self.language = QComboBox(self)
        self.language.setToolTip(lang['SETTINGS']['language_tt'])
        self.language.activated.connect(self._item_select)
        self._box_fill()
        # setup 'Load placed' checkbox
        self.load_placed = QCheckBox(lang['SETTINGS']['load_placed'], self)
        self.load_placed.setToolTip(lang['SETTINGS']['load_placed_tt'])
        if settings['MAIN']['load_placed'].lower() in ('true', 'yes', 'on'):
            self.load_placed.setChecked(True)
        # setup 'Languages' lebel
        self.label = QLabel(lang['SETTINGS']['label'], self)
        self.label.setAlignment(Qt.AlignCenter)
        # setup widgets delete button
        self.del_button = QPushButton(lang['SETTINGS']['del_button'], self)
        self.del_button.setToolTip(lang['SETTINGS']['del_button_tt'])
        self.del_button.clicked.connect(self._show_del_widgets)
        # setup 'Save' button
        self.save_button = QPushButton(lang['SETTINGS']['save_button'], self)
        self.save_button.setToolTip(lang['SETTINGS']['save_button_tt'])
        self.save_button.clicked.connect(self._save)
        # setup 'Cancel' button
        self.cancel_button = QPushButton(lang['SETTINGS']['cancel_button'],
                                         self)
        self.cancel_button.setToolTip(lang['SETTINGS']['cancel_button_tt'])
        self.cancel_button.clicked.connect(self._cancel)
        # setup h box layout
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.save_button)
        self.h_box.addWidget(self.cancel_button)
        # setup grid layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.label, 0, 0)
        self.grid.addWidget(self.language, 0, 1)
        self.grid.addWidget(self.load_placed, 1, 0, 1, 2)
        self.grid.addWidget(self.del_button, 2, 0, 1, 2)
        self.grid.addLayout(self.h_box, 3, 0, 1, 2)
        self.setLayout(self.grid)
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
        mbox = QMessageBox(QMessageBox.Warning,
                           self.lang['SETTINGS']['warn_title'],
                           self.lang['SETTINGS']['warn_text'], QMessageBox.Ok,
                           self)
        mbox.setWindowIcon(QIcon(SUCCESS))
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
