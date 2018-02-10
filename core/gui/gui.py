"""Main GUI."""
import os
import sys
import traceback
from distutils.util import strtobool
from configparser import ConfigParser
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem
from PyQt5.QtWidgets import QPushButton, QCheckBox, QStatusBar, QListWidget
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu
from PyQt5.QtCore import Qt, QRect, QEvent, QLocale
from PyQt5.QtGui import QIcon
from core.paths import CONF_SETTINGS, DeWidgetsIcon, ERROR, LOCK_FILE, DELETE
from core.paths import LOAD, UNLOAD, RELOAD, SHOW, HIDE, SETTINGS, EXIT, LANGS
from core.paths import C_LANGS
from core.gui import add_new
from core.gui.help import Help, TextViewer
from core.gui.move import Move
from core.gui.settings import Settings
from core.manager import WidgetManager
from core.utils import try_except

settings = ConfigParser()
"""ConfigParser, settings dict"""
lang = ConfigParser()
"""ConfigParser, locale dict"""
c_lang = ConfigParser()
"""ConfigParser, locale dict for custom widgets"""
manager = WidgetManager(lang, c_lang, sys.modules[__name__])
"""WidgetManager object"""
app = None
"""QApplication object"""
main = None
"""Main object"""


def __init__(main_app):
    """start app"""
    global app, main
    # load configs
    settings.read(CONF_SETTINGS, 'utf-8')
    lang.read(os.path.join(LANGS, settings['MAIN']['locale'] + '.conf'),
              'utf-8')
    cl_file = os.path.join(C_LANGS, settings['MAIN']['locale'] + '.conf')
    if os.path.isfile(cl_file):
        c_lang.read(cl_file, 'utf-8')
    if os.path.isfile(LOCK_FILE):  # check lock
        with open(LOCK_FILE) as lock:
            try:
                os.kill(int(lock.read()), 0)
            except OSError:
                pass
            else:
                _show_error()
                sys.exit(0)
    # setup locale
    QLocale.setDefault(QLocale(QLocale.__dict__[lang['LANG']['language']],
                               QLocale.__dict__[lang['LANG']['country']]))
    # create lock file
    with open(LOCK_FILE, 'w') as lock:
        lock.write(str(os.getpid()))
    # init
    app = main_app
    main = Main()
    add_new.__init__(lang, main)
    # load widgets
    if bool(strtobool(settings['MAIN']['load_placed'])):
        manager.load_placed()  # placed only
    else:
        manager.load_all()  # all widgets
    main._list_fill()
    if manager.is_placed():
        return  # if found placed widgets - no show main window
    main.show()  # if no placed widgets, show window


class Main(QMainWindow):
    """main window"""
    def __init__(self):
        super().__init__()
        icon = QIcon(DeWidgetsIcon)
        # setup window
        self.setWindowTitle(lang['MAIN']['title'])
        self.setFixedSize(520, 262)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |
                            Qt.WindowCloseButtonHint)
        self.setWindowIcon(icon)
        # setup vars
        self.help_window = None
        self.settings_win = None
        self.move_window = None
        # setup list
        self.list = QListWidget(self)
        self.list.setGeometry(QRect(0, 0, 281, 231))
        self.list.setSpacing(2)
        self.list.itemClicked.connect(self._list_click)
        self.list.itemDoubleClicked.connect(self._list_double_click)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._show_list_menu)
        # setup list context menu
        self.list_menu = QMenu(self)
        load_action = self.list_menu.addAction(QIcon(LOAD),
                                               lang['LIST_MENU']['load'])
        load_action.setToolTip(lang['LIST_MENU']['load_tt'])
        load_action.triggered.connect(self._load_not_placed)
        unload_action = self.list_menu.addAction(QIcon(UNLOAD),
                                                 lang['LIST_MENU']['unload'])
        unload_action.setToolTip(lang['LIST_MENU']['unload_tt'])
        unload_action.triggered.connect(self._unload_not_placed)
        self.list_menu.addSeparator()
        reload_action = self.list_menu.addAction(QIcon(RELOAD),
                                                 lang['LIST_MENU']['reload'])
        reload_action.setToolTip(lang['LIST_MENU']['reload_tt'])
        reload_action.triggered.connect(self._reload)
        # setup 'Add' button
        self.add_button = QPushButton(lang['MAIN']['add_button'], self)
        self.add_button.setToolTip(lang['MAIN']['add_button_tt'])
        self.add_button.setGeometry(QRect(300, 5, 94, 27))
        self.add_button.clicked.connect(self._add_widget)
        # setup 'Delete' button
        self.del_button = QPushButton(lang['MAIN']['del_button'], self)
        self.del_button.setToolTip(lang['MAIN']['del_button_tt'])
        self.del_button.setGeometry(QRect(410, 5, 94, 27))
        self.del_button.clicked.connect(self._show_del)
        # setup 'Configure' button
        self.wset_button = QPushButton(lang['MAIN']['wset_button'], self)
        self.wset_button.setToolTip((lang['MAIN']['wset_button_tt']))
        self.wset_button.setGeometry(QRect(300, 35, 94, 27))
        self.wset_button.clicked.connect(self._show_widget_settings)
        # setup 'Move' button
        self.move_button = QPushButton(lang['MAIN']['move_button'], self)
        self.move_button.setToolTip(lang['MAIN']['move_button_tt'])
        self.move_button.setGeometry(QRect(410, 35, 94, 27))
        self.move_button.clicked.connect(self._show_move)
        # setup 'edit mode' checkbox
        self.edit_mode_checkbox = QCheckBox(lang['MAIN']['edit_mode'], self)
        self.edit_mode_checkbox.setToolTip(lang['MAIN']['edit_mode_tt'])
        self.edit_mode_checkbox.setGeometry(QRect(300, 75, 240, 20))
        self.edit_mode_checkbox.clicked.connect(self._edit_mode)
        # setup 'Add new' button
        self.new_button = QPushButton(lang['MAIN']['new_button'], self)
        self.new_button.setToolTip(lang['MAIN']['new_button_tt'])
        self.new_button.setGeometry(QRect(355, 130, 94, 27))
        self.new_button.clicked.connect(self._show_add_new)
        # setup 'Settings' button
        self.settings_button = QPushButton(lang['MAIN']['settings_button'],
                                           self)
        self.settings_button.setToolTip(lang['MAIN']['settings_button_tt'])
        self.settings_button.setGeometry(QRect(300, 160, 94, 27))
        self.settings_button.clicked.connect(self._show_settings)
        # setup 'Help' button
        self.help_button = QPushButton(lang['MAIN']['help_button'], self)
        self.help_button.setToolTip(lang['MAIN']['help_button'])
        self.help_button.setGeometry(QRect(410, 160, 94, 27))
        self.help_button.clicked.connect(self._show_help)
        # setup 'Exit' button
        self.exit_button = QPushButton(lang['MAIN']['exit_button'], self)
        self.exit_button.setToolTip(lang['MAIN']['exit_button_tt'])
        self.exit_button.setGeometry(QRect(355, 190, 94, 27))
        self.exit_button.clicked.connect(app.quit)
        # setup status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.statusBar().showMessage(lang['STATUS']['first'])
        # setup tray
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip(lang['MAIN']['title'])
        self.tray.activated.connect(self._visible)
        menu = QMenu(self)
        show_action = menu.addAction(QIcon(SHOW), lang['TRAY']['show_action'])
        show_action.setToolTip(lang['TRAY']['show_action_tt'])
        show_action.triggered.connect(self.showNormal)
        hide_action = menu.addAction(QIcon(HIDE), lang['TRAY']['hide_action'])
        hide_action.setToolTip(lang['TRAY']['hide_action_tt'])
        hide_action.triggered.connect(self._hide_widgets)
        settings_action = menu.addAction(QIcon(SETTINGS),
                                         lang['TRAY']['settings_action'])
        settings_action.setToolTip(lang['TRAY']['settings_action'])
        settings_action.triggered.connect(self._show_settings)
        menu.addSeparator()
        exit_action = menu.addAction(QIcon(EXIT), lang['TRAY']['exit_action'])
        exit_action.setToolTip(lang['TRAY']['exit_action_tt'])
        exit_action.triggered.connect(app.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()
        # set enabled
        self.__change_enabled()

    def __change_enabled(self):
        item = self.list.currentItem()
        if not item:
            self.add_button.setEnabled(False)
            self.del_button.setEnabled(False)
            self.wset_button.setEnabled(False)
            self.move_button.setEnabled(False)
            return
        if manager.config.is_placed(item.text()):
            self.add_button.setEnabled(False)
            self.del_button.setEnabled(True)
            self.wset_button.setEnabled(True)
            self.move_button.setEnabled(True)
        else:
            self.add_button.setEnabled(True)
            self.del_button.setEnabled(False)
            self.wset_button.setEnabled(False)
            self.move_button.setEnabled(False)
        if self.list.size().isEmpty():
            self.edit_mode_checkbox.setEnabled(False)
        elif manager.is_placed():
            self.edit_mode_checkbox.setEnabled(True)

    @try_except()
    def _add_widget(self, checked):
        item = self.list.currentItem()
        # setup widget
        manager.config.create(item.text())
        r = manager.load(os.path.basename(manager.paths[item.text()])[:-3],
                         False)
        if not r:
            return
        widget = manager.widgets[item.text()]
        widget.place()
        widget.setWindowFlags(Qt.CustomizeWindowHint |
                              Qt.WindowStaysOnBottomHint | Qt.Tool)
        widget.show()
        # edit config
        manager.config.add(widget.info.NAME)
        manager.config.save()
        # change item font
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        # changing enabled
        self.__change_enabled()

    @try_except()
    def _show_help(self, checked):
        self.help_window = Help(lang)

    def _list_fill(self):
        self.list.clear()
        for info in manager.info.values():
            try:
                item = QListWidgetItem(self.list)
                item.setIcon(info.ICON)
                item.setText(info.NAME)
                item.setToolTip(info.DESCRIPTION)
                if manager.config.is_placed(info.NAME):
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.list.addItem(item)
            except:
                print(traceback.format_exc())

    @try_except()
    def _list_double_click(self, item):
        self.item_info = ItemInfo(item.text())

    @try_except()
    def _list_click(self, item):
        self.__change_enabled()
        self.statusBar().showMessage(manager.info[item.text()].DESCRIPTION)

    @try_except()
    def _show_add_new(self, checked):
        names = add_new.install()
        for name in names:
            try:
                manager.load(name)
            except:
                print(traceback.format_exc())
        if names:
            self._list_fill()
        self.__change_enabled()

    @try_except()
    def _show_settings(self, checked):
        self.settings_win = Settings(lang, self, settings)

    @try_except()
    def _edit_mode(self, checked):
        for widget in manager.widgets.values():
            try:
                if widget.isHidden():
                    continue
                if self.edit_mode_checkbox.isChecked():  # on
                    widget.setWindowFlags(Qt.WindowMinimizeButtonHint |
                                          Qt.WindowStaysOnBottomHint | Qt.Tool)
                    widget.show()
                    self.statusBar().showMessage(lang['STATUS']['edit_on'])
                else:  # off
                    widget.setWindowFlags(Qt.CustomizeWindowHint |
                                          Qt.WindowStaysOnBottomHint | Qt.Tool)
                    widget.show()
                    self.statusBar().showMessage(lang['STATUS']['first'])
            except:
                print(traceback.format_exc())
        # save
        manager.edit_mode(self.edit_mode_checkbox.isChecked())
        if not self.edit_mode_checkbox.isChecked():
            manager.config.save()

    @try_except()
    def _show_del(self, checked):
        # check item
        item = self.list.currentItem()
        # setup box
        mbox = QMessageBox(QMessageBox.Question, lang['DELETE']['title'],
                           lang['DELETE']['question'], QMessageBox.Yes |
                           QMessageBox.No | QMessageBox.Cancel, self)
        mbox.setWindowIcon(QIcon(DELETE))
        # setup 'Yes' button
        yes = mbox.button(QMessageBox.Yes)
        yes.setText(lang['DELETE']['yes'])
        yes.setToolTip(lang['DELETE']['yes_tt'])
        # setup 'No' button
        no = mbox.button(QMessageBox.No)
        no.setText(lang['DELETE']['no'])
        no.setToolTip(lang['DELETE']['no_tt'])
        # setup 'Cancel' button
        cancel = mbox.button(QMessageBox.Cancel)
        cancel.setText(lang['DELETE']['cancel'])
        cancel.setToolTip(lang['DELETE']['cancel_tt'])
        # deleting
        key = mbox.exec()
        if key == QMessageBox.Yes:
            manager.remove_from_desktop(item.text(), True)
        elif key == QMessageBox.No:
            manager.remove_from_desktop(item.text())
        else:
            return
        # change item font
        font = item.font()
        font.setBold(False)
        item.setFont(font)
        # changing enabled
        self.__change_enabled()

    @try_except()
    def _show_widget_settings(self, checked):
        manager.widgets[self.list.currentItem().text()].show_settings()

    @try_except()
    def _show_move(self, checked):
        self.move_window = Move(
            manager.widgets[self.list.currentItem().text()], manager)

    @try_except()
    def _visible(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isHidden():
                self.showNormal()
            else:
                self.setHidden(True)

    @try_except()
    def _hide_widgets(self, checked):
        for name in manager.widgets:
            try:
                if manager.widgets[name].isHidden():
                    manager.widgets[name].hide_event(False)
                    manager.widgets[name].setHidden(False)
                else:
                    manager.widgets[name].hide_event(True)
                    manager.widgets[name].setHidden(True)
            except:
                print(traceback.format_exc())

    @try_except()
    def _show_list_menu(self, point):
        self.list_menu.exec(self.list.mapToGlobal(point))

    @try_except()
    def _unload_not_placed(self, point):
        manager.del_data_no_placed()
        self._list_fill()
        self.__change_enabled()

    @try_except()
    def _load_not_placed(self, point):
        manager.load_placed(False)
        self._list_fill()
        self.__change_enabled()

    @try_except()
    def _reload(self, point):
        manager.unload_all()
        if bool(strtobool(settings['MAIN']['load_placed'])):
            manager.load_placed()
        else:
            manager.load_all()
        self._list_fill()
        self.__change_enabled()

    @try_except()
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() and Qt.WindowMinimized:
                event.ignore()
                self.setHidden(True)


class ItemInfo(TextViewer):
    """view item info"""
    def __init__(self, name):
        # init
        super().__init__(name, lang['ITEM']['exit_button'],
                         lang['ITEM']['exit_button_tt'])
        # setup
        info = manager.info[name]
        self.setWindowIcon(info.ICON)
        kwargs = {
            'name': name, 'version': info.VERSION,
            'description': info.DESCRIPTION, 'author': info.AUTHOR,
            'email': info.EMAIL, 'link': info.URL, 'help': info.HELP
        }
        self.text.setHtml(lang['ITEM']['html'].format(**kwargs))
        # show
        self.show()


def _show_error():
    mbox = QMessageBox(QMessageBox.Critical, lang['RUNNING']['title'],
                       lang['RUNNING']['text'], QMessageBox.Ok)
    mbox.setWindowIcon(QIcon(ERROR))
    ok = mbox.button(QMessageBox.Ok)
    ok.setText(lang['RUNNING']['ok_button'])
    ok.setToolTip(lang['RUNNING']['ok_button_tt'])
    mbox.exec()
