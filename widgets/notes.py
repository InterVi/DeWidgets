import os
import json
import base64
from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QListWidget
from PyQt5.QtWidgets import QListWidgetItem, QCheckBox, QMessageBox, QComboBox
from PyQt5.QtWidgets import QLabel, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from core.manager import Widget, WidgetInfo
from core.gui.move import Move
from core.paths import RES, SETTINGS, DELETE, SUCCESS
from core.utils import try_except, print_stack_trace


class Note(QWidget):
    def __init__(self, main, index):
        QWidget.__init__(self)
        self.main = main
        self.index = index
        # setup window
        self.setWindowIcon(main.info.ICON)
        if index > 0:
            self.setWindowFlags(Qt.CustomizeWindowHint |
                                Qt.WindowStaysOnBottomHint | Qt.Tool)
        # setup text edit
        self.text_edit = QTextEdit(self)
        self.text_edit.textChanged.connect(self._text_changed)
        # setup v box layout
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(self.text_edit)
        self.setLayout(self.grid)

    def _init(self):
        self.setStyleSheet(self.main.get_style(self.index))
        if self.index:
            if len(self.main.sizes) >= self.index:
                size = self.main.sizes[self.index - 1]
                self.resize(size['width'], size['height'])
                self.move(size['x'], size['y'])
                self.setWindowOpacity(size['opacity'])
        if len(self.main.notes) >= self.index + 1:
            self.text_edit.setPlainText(self.main.notes[self.index])
            self.setWindowTitle(self.text_edit.toPlainText()[:40].strip())
        else:
            self.setWindowTitle(self.main.info.NAME)

    @try_except()
    def _text_changed(self):
        if self.main.notes[self.index] == self.text_edit.toPlainText():
            return
        self.main.notes[self.index] = self.text_edit.toPlainText()
        self.main.save_conf()


class Info(WidgetInfo):
    def __init__(self, lang):
        WidgetInfo.__init__(self, lang)
        self.lang = lang['NOTES']
        self.NAME = 'Simple Notes'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'notes', 'icon.png'))


class Main(Widget, Note):
    def __init__(self, widget_manager, info):
        # init
        Widget.__init__(self, widget_manager, info)
        Note.__init__(self, self, 0)
        self.conf = {}
        self.lang = info.lang
        # setup vars
        self.settings_win = None
        self.__setup_vars()

    def __setup_vars(self):
        self.notes = [self.lang['note']]
        self.styles = ['white.css']
        self.sizes = []  # -1 index offset
        self.widgets = []  # -1 index offset (0 - main window)
        self.editable = True
        self.style_names = json.loads(self.lang['styles'])
        self.style_keys = {}
        for item in self.style_names.items():
            self.style_keys[item[1]] = item[0]

    def save_conf(self):
        b_notes = []
        for note in self.notes:
            b_notes.append(base64.b64encode(note.encode('utf-8')
                                            ).decode('ASCII'))
        self.conf['notes'] = json.dumps(b_notes)
        self.conf['styles'] = json.dumps(self.styles)
        self.sizes.clear()
        for widget in self.widgets:
            size = {
                'width': widget.width(), 'height': widget.height(),
                'x': widget.x(), 'y': widget.y(),
                'opacity': widget.windowOpacity()
            }
            self.sizes.append(size)
        self.conf['sizes'] = json.dumps(self.sizes)
        self.conf['editable'] = json.dumps(self.editable)
        if 'hot_saves' in self.conf and self.conf['hot_saves'] == 'true':
            self.widget_manager.config.save()

    def get_style(self, index=0) -> str:
        path = os.path.join(RES, 'notes', 'css', self.styles[index])
        with open(path, encoding='utf-8') as file:
            return file.read()

    def _load_settings(self):
        self.conf = self.widget_manager.get_config(self.info.NAME)
        if 'notes' in self.conf:
            self.notes.clear()
            b_notes = json.loads(self.conf['notes'])
            for b_note in b_notes:
                self.notes.append(base64.b64decode(b_note).decode('utf-8'))
        if 'styles' in self.conf:
            self.styles = json.loads(self.conf['styles'])
        if 'sizes' in self.conf:
            self.sizes = json.loads(self.conf['sizes'])
        if 'editable' in self.conf:
            self.editable = json.loads(self.conf['editable'])
        self._init()

    def _load_widgets(self):
        for i in range(len(self.notes)):
            if i == 0:
                continue
            try:
                note = Note(self, i)
                note._init()
                note.show()
                self.widgets.append(note)
            except:
                print_stack_trace()()

    def boot(self):
        self._load_settings()
        self._load_widgets()

    def place(self):
        self._load_settings()
        self._load_widgets()

    def hide_event(self, state):
        for widget in self.widgets:
            widget.setHidden(state)

    def edit_mode(self, mode):
        for widget in self.widgets:
            if mode:
                widget.setWindowFlags(Qt.WindowMinimizeButtonHint |
                                      Qt.WindowStaysOnBottomHint | Qt.Tool)
                widget.show()
            else:
                widget.setWindowFlags(Qt.CustomizeWindowHint |
                                      Qt.WindowStaysOnBottomHint | Qt.Tool)
                widget.show()
        self.save_conf()

    def unload(self):
        self.save_conf()

    def remove(self):
        for widget in self.widgets:
            widget.destroy()

    def purge(self):
        self.remove()
        self.__setup_vars()

    @try_except()
    def show_settings(self):
        self.settings_win = Settings(self)


class Settings(QWidget):
    def __init__(self, main):
        QWidget.__init__(self)
        self.main = main
        self.note_settings = None
        # setup window
        self.setWindowIcon(QIcon(SETTINGS))
        self.setWindowTitle(main.lang['settings_title'])
        self.resize(400, 400)
        # setup list
        self.list = QListWidget(self)
        self.list.setWordWrap(True)
        self.list.itemClicked.connect(self.__change_enabled)
        self.list.itemDoubleClicked.connect(self._list_double_click)
        self._list_fill()
        # setup 'Editable' checkbox
        self.editable = QCheckBox(main.lang['settings_editable'], self)
        self.editable.setToolTip(main.lang['settings_editable_tt'])
        self.editable.setChecked(main.editable)
        self.editable.stateChanged.connect(self._editable_changed)
        # setup 'Hot save' checkbox
        self.hot_save = QCheckBox(main.lang['save_checkbox'], self)
        self.hot_save.setToolTip(main.lang['save_checkbox_tt'])
        if 'hot_saves' in main.conf:
            self.hot_save.setChecked(json.loads(main.conf['hot_saves']))
        self.hot_save.stateChanged.connect(self._save_changed)
        # setup 'Delete' button
        self.delete_button = QPushButton(main.lang['settings_delete_button'],
                                         self)
        self.delete_button.setToolTip(main.lang['settings_delete_button_tt'])
        self.delete_button.clicked.connect(self._delete)
        # setup 'Add' button
        self.add_button = QPushButton(main.lang['settings_add_button'], self)
        self.add_button.setToolTip(main.lang['settings_add_button_tt'])
        self.add_button.clicked.connect(self._add)
        # setup 'Close' button
        self.close_button = QPushButton(main.lang['settings_close_button'],
                                        self)
        self.close_button.setToolTip(main.lang['settings_close_button_tt'])
        self.close_button.clicked.connect(self.close)
        # setup layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.list, 0, 0, 1, 2)
        self.grid.addWidget(self.editable, 1, 0)
        self.grid.addWidget(self.hot_save, 1, 1)
        self.grid.addWidget(self.delete_button, 2, 0, 1, 2)
        self.grid.addWidget(self.add_button, 3, 0, 1, 2)
        self.grid.addWidget(self.close_button, 4, 0, 1, 2)
        self.setLayout(self.grid)
        # show
        self.__change_enabled()
        self.show()

    def __change_enabled(self):
        if self.list.currentItem():
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)

    @try_except()
    def _list_fill(self):
        self.list.clear()
        item = QListWidgetItem(
            self.main.text_edit.toPlainText()[:40].strip(), self.list
        )
        if not item.text():
            item.setText('-')
        self.list.addItem(item)
        for widget in self.main.widgets:
            item = QListWidgetItem(
                widget.text_edit.toPlainText()[:40].strip(), self.list
            )
            if not item.text():
                item.setText('-')
            self.list.addItem(item)

    @try_except()
    def _list_double_click(self, checked):
        self.note_settings = NoteSettings(self.main, self)

    @try_except()
    def _editable_changed(self, state):
        self.main.editable = self.editable.isChecked()
        self.main.save_conf()
        self.main.text_edit.setEnabled(self.main.editable)
        for widget in self.main.widgets:
            widget.setEnabled(self.main.editable)

    @try_except()
    def _save_changed(self, state):
        self.main.conf['hot_saves'] = json.dumps(self.hot_save.isChecked())
        self.main.save_conf()

    @try_except()
    def _delete(self, checked):
        if self.list.count() <= 1:
            return
        # confirm dialog
        mbox = QMessageBox(QMessageBox.Question,
                           self.main.lang['delete_title'],
                           self.main.lang['delete_text'],
                           QMessageBox.Yes | QMessageBox.No, self)
        mbox.setWindowIcon(QIcon(DELETE))
        mbox.setInformativeText(self.main.lang['delete_inf'].format(
            self.list.currentItem().text()))
        yes = mbox.button(QMessageBox.Yes)
        yes.setText(self.main.lang['delete_yes_button'])
        yes.setToolTip(self.main.lang['delete_yes_button_tt'])
        no = mbox.button(QMessageBox.No)
        no.setText(self.main.lang['delete_no_button'])
        no.setToolTip(self.main.lang['delete_no_button_tt'])
        if mbox.exec() != QMessageBox.Yes:
            return
        # deleting process
        row = self.list.currentRow()
        if row == 0:  # change main win
            self.main.notes[0] = self.main.notes[1]
            del self.main.notes[1]
            self.main.text_edit.setPlainText(self.main.notes[0])
            self.main.styles[0] = self.main.styles[1]
            del self.main.styles[1]
            self.main.setStyleSheet(self.main.get_style(0))
            size = self.main.sizes[0]
            self.main.resize(size['width'], size['height'])
            self.main.move(size['x'], size['y'])
            self.main.setWindowOpacity(size['opacity'])
            del self.main.sizes[0]
            self.main.widgets[0].destroy()
            del self.main.widgets[0]
            self.main.show()
            self.main.widget_manager.edit_mode(False, self.main.info.NAME)
        else:  # remove child win
            del self.main.notes[row]
            del self.main.styles[row]
            del self.main.sizes[row - 1]
            self.main.widgets[row - 1].destroy()
            del self.main.widgets[row - 1]
        self.main.save_conf()
        self._list_fill()

    @try_except()
    def _add(self, checked):
        # adding
        self.main.notes.append(self.main.lang['note'])
        self.main.styles.append('white.css')
        note = Note(self.main, self.list.count())
        note._init()
        note.show()
        self.main.widgets.append(note)
        self.list.addItem(QListWidgetItem(self.main.lang['note'],
                                          self.list))
        self.list.setCurrentRow(self.list.count() - 1)
        self.main.save_conf()
        # show success alert
        mbox = QMessageBox(QMessageBox.Information,
                           self.main.lang['success_title'],
                           self.main.lang['success_text'], QMessageBox.Ok,
                           self)
        mbox.setWindowIcon(QIcon(SUCCESS))
        ok = mbox.button(QMessageBox.Ok)
        ok.setText(self.main.lang['success_ok_button'])
        ok.setToolTip(self.main.lang['success_ok_button_tt'])
        mbox.exec()


class NoteSettings(QWidget):
    def __init__(self, main, settings):
        QWidget.__init__(self)
        self.main = main
        self.settings = settings
        self.move_win = None
        # setup window
        self.setWindowTitle(main.lang['item_title'].format(settings.list.item(
            settings.list.currentRow()).text()))
        self.setWindowIcon(main.info.ICON)
        self.resize(400, 400)
        # setup text edit
        self.text_edit = QTextEdit(self)
        self.row = settings.list.currentRow()
        if self.row == 0:
            self.text_edit.setPlainText(main.text_edit.toPlainText())
        else:
            self.text_edit.setPlainText(
                main.widgets[self.row-1].text_edit.toPlainText())
        self.text_edit.textChanged.connect(self._text_changed)
        # setup styles label
        self.label = QLabel(main.lang['item_label'], self)
        self.label.setAlignment(Qt.AlignCenter)
        # setup styles combobox
        self.styles_list = QComboBox(self)
        self.styles_list.addItems(main.style_names.values())
        self.styles_list.setToolTip(main.lang['item_styles_tt'])
        self.styles_list.setCurrentText(
            main.style_names[main.styles[self.row]])
        self.styles_list.activated.connect(self._style_select)
        # setup 'Move' button
        self.move_button = QPushButton(main.lang['move_button'], self)
        self.move_button.setToolTip(main.lang['move_button_tt'])
        self.move_button.clicked.connect(self._show_move)
        # setup 'Close' button
        self.close_button = QPushButton(main.lang['item_close_button'], self)
        self.close_button.setToolTip(main.lang['item_close_button_tt'])
        self.close_button.clicked.connect(self.close)
        # setup layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.text_edit, 0, 0, 1, 2)
        self.grid.addWidget(self.label, 1, 0)
        self.grid.addWidget(self.styles_list, 1, 1)
        self.grid.addWidget(self.move_button, 2, 0, 1, 2)
        self.grid.addWidget(self.close_button, 3, 0, 1, 2)
        self.setLayout(self.grid)
        # show
        self.show()

    @try_except()
    def _text_changed(self):
        if self.row == 0:
            self.main.text_edit.setPlainText(self.text_edit.toPlainText())
        else:
            self.main.widgets[self.row - 1].text_edit.setPlainText(
                self.text_edit.toPlainText())
        self.main.save_conf()
        self.settings._list_fill()

    @try_except()
    def _style_select(self, index):
        self.main.styles[self.row] = \
            self.main.style_keys[self.styles_list.currentText()]
        style = self.main.get_style(self.row)
        if self.row == 0:
            self.main.setStyleSheet(style)
            self.main.show()
        else:
            self.main.widgets[self.row - 1].setStyleSheet(style)
            self.main.widgets[self.row - 1].show()
        self.main.save_conf()

    @try_except()
    def _show_move(self, checked):
        if self.row == 0:
            win = self.main
        else:
            win = self.main.widgets[self.row - 1]
        self.move_win = Move(win, self.main.widget_manager)
