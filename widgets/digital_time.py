import os
import json
import base64
from distutils.util import strtobool
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QCheckBox, QPushButton, QSpinBox, QLineEdit
from PyQt5.QtWidgets import QColorDialog, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QTimer
from core.api import Widget, WidgetInfo
from core.gui.edit import Edit
from core.paths import RES, SETTINGS, SUCCESS, DELETE
from core.utils import try_except, print_stack_trace
from core.gui.drag import mouse_enter


def get_time(utc=False, format='%X', hours=0, minutes=0, seconds=0) -> str:
    """Get formatted time string.

    :param utc: true - use UTC time, false - local
    :param format: template for formatter (default: "%X")
    :param hours: hours offset
    :param minutes: minutes offset
    :param seconds: seconds offset
    :return: str, formatted time string
    """
    dt = datetime.utcnow() if utc else datetime.today()
    stamp = dt.timestamp() + (hours * 60 * 60) + (minutes * 60) + seconds
    return datetime.fromtimestamp(stamp).strftime(format)


def strf_validate(strf) -> bool:
    """Format validator.

    :param strf: string format for use datetime.strftime
    :return: True - if format correctly
    """
    try:
        datetime.strftime(datetime.now(), strf)
        return True
    except ValueError:
        return False


class DTime(QWidget):
    def __init__(self, main, index):
        """

        :param main: Main object
        :param index: int, index in lists
        """
        # init
        QWidget.__init__(self)
        self.enterEvent = mouse_enter(main.widget_manager, self
                                      )(self.enterEvent)
        self.main = main
        self.index = index
        # setup window
        self.setWindowFlags(Qt.CustomizeWindowHint |
                            Qt.WindowStaysOnBottomHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # setup label
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        # setup v box layout
        self.v_box = QVBoxLayout(self)
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.addWidget(self.label)
        self.setLayout(self.v_box)

    @try_except()
    def _init(self):
        name = self.main.names[self.index]
        self.setWindowIcon(self.main.info.ICON)
        if self.index > 0:
            self.setWindowTitle(name)
            if len(self.main.sizes) >= self.index:
                size = self.main.sizes[self.index - 1]
                self.resize(size['width'], size['height'])
                self.move(size['x'], size['y'])
                self.setWindowOpacity(size['opacity'])
        self.setToolTip(name)
        self.label.setToolTip(name)
        palette = self.label.palette()
        palette.setColor(QPalette.WindowText,
                         QColor(self.main.colors[self.index]))
        self.label.setPalette(palette)
        self._update_time()

    @try_except()
    def _update_time(self):
        self.label.setText(get_time(self.main._utc,
                                    self.main.times[self.index],
                                    *self.main.offsets[self.index]))

    @try_except()
    def resizeEvent(self, event):
        screen = self.main.widget_manager.main_gui.app.desktop(). \
            screenGeometry()
        if event.size().width() >= screen.width() or \
                event.size().height() >= screen.height():  # break loop
            return
        h_size = int(self.height() / self.main._hdi)
        w_size = int(self.width() / self.main._wdi)
        size = h_size
        if w_size > h_size:
            size = w_size
        font = self.label.font()
        font.setPointSize(int(size / self.main._sdi))
        font.setBold(True)
        self.label.setFont(font)


class Info(WidgetInfo):
    def __init__(self, lang):
        WidgetInfo.__init__(self, lang)
        self.lang = lang['DIGITAL_TIME']
        self.NAME = 'Digital Time'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'dtime', 'icon.png'))


class Main(Widget, DTime):
    def __init__(self, widget_manager, info):
        # init
        Widget.__init__(self, widget_manager, info)
        DTime.__init__(self, self, 0)
        self.conf = {}
        self.lang = info.lang
        self.settings_win = None
        # setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timeout)
        self.destroyed.connect(self.timer.stop)
        # setup vars
        self.__setup_vars()

    def __setup_vars(self):
        self.times = ['%X']
        self.offsets = [(0, 0, 0)]
        self.sizes = []  # -1 index offset
        self.names = [self.lang['names']]
        self.colors = ['#000']
        self.widgets = []  # -1 index offset (0 - main window)
        self._hdi = 2
        self._wdi = 4
        self._sdi = 2
        self._msec = 1000
        self._utc = False

    def _load_settings(self):
        self.conf = self.widget_manager.get_config(self.info.NAME)
        if 'times' in self.conf:
            self.times = json.loads(
                base64.b64decode(self.conf['times']).decode('utf-8'))
        if 'offsets' in self.conf:
            self.offsets = json.loads(self.conf['offsets'])
        if 'names' in self.conf:
            self.names.clear()
            b_names = json.loads(self.conf['names'])
            for b_name in b_names:
                self.names.append(base64.b64decode(b_name).decode('utf-8'))
        if 'colors' in self.conf:
            self.colors = json.loads(self.conf['colors'])
        if 'sizes' in self.conf:
            self.sizes = json.loads(self.conf['sizes'])
        if 'hdi' in self.conf:
            self._hdi = int(self.conf['hdi'])
        if 'wdi' in self.conf:
            self._wdi = int(self.conf['wdi'])
        if 'sdi' in self.conf:
            self._sdi = int(self.conf['sdi'])
        if 'msec' in self.conf:
            self._msec = int(self.conf['msec'])
        if 'utc' in self.conf:
            self._utc = bool(strtobool(self.conf['utc']))
        self._init()

    def _load_widgets(self):
        for i in range(len(self.times)):
            try:
                if i == 0:
                    DTime._init(self)
                    continue
                dtime = DTime(self, i)
                dtime.setAccessibleName(self.info.NAME)
                dtime._init()
                dtime.show()
                self.widgets.append(dtime)
            except:
                print_stack_trace()()

    @try_except()
    def _timeout(self):
        self._update_time()
        for widget in self.widgets:
            widget._update_time()

    @try_except()
    def save_settings(self):
        self.conf['times'] = base64.b64encode(
            json.dumps(self.times).encode('utf-8')).decode('ASCII')
        self.conf['offsets'] = json.dumps(self.offsets)
        b_names = []
        for name in self.names:
            b_names.append(base64.b64encode(name.encode('utf-8')
                                            ).decode('ASCII'))
        self.conf['names'] = json.dumps(b_names)
        self.conf['colors'] = json.dumps(self.colors)
        self.sizes.clear()
        for widget in self.widgets:
            size = {
                'width': widget.width(), 'height': widget.height(),
                'x': widget.x(), 'y': widget.y(),
                'opacity': widget.windowOpacity()
            }
            self.sizes.append(size)
        self.conf['sizes'] = json.dumps(self.sizes)
        self.conf['hdi'] = str(self._hdi)
        self.conf['wdi'] = str(self._wdi)
        self.conf['sdi'] = str(self._sdi)
        self.conf['msec'] = str(self._msec)
        self.conf['utc'] = str(self._utc)

    def boot(self):
        self._load_settings()
        self._load_widgets()

    def place(self):
        self.resize(100, 100)
        self._load_settings()
        self._load_widgets()

    def hide_event(self, mode):
        for widget in self.widgets:
            widget.setHidden(mode)

    def edit_mode(self, mode):
        if mode:
            return
        self.save_settings()

    def unload(self):
        self.save_settings()

    def remove(self):
        for widget in self.widgets:
            widget.destroy()

    def purge(self):
        self.remove()
        self.__setup_vars()

    @try_except()
    def show_settings(self):
        self.settings_win = Settings(self)

    @try_except()
    def showEvent(self, event):
        self._timeout()
        self.timer.start(self._msec)

    @try_except()
    def hideEvent(self, event):
        self.timer.stop()

    def closeEvent(self, event):
        self.hideEvent(event)


class Settings(QWidget):
    def __init__(self, main):
        """

        :param main: Main object
        """
        QWidget.__init__(self)
        self.main = main
        self.lang = main.lang
        self.time_edit = None
        # setup window
        self.setWindowIcon(QIcon(SETTINGS))
        self.setWindowTitle(main.lang['settings_title'])
        self.resize(300, 400)
        # setup list
        self.list = QListWidget(self)
        self.list.setToolTip(main.lang['settings_list_tt'])
        self.list.itemDoubleClicked.connect(self._item_double_clicked)
        self._list_fill()
        # setup time label
        self.time_label = QLabel(get_time(self.main._utc), self)
        self.time_label.setAlignment(Qt.AlignCenter)
        font = self.time_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.time_label.setFont(font)
        self.time_label.setToolTip(main.lang['display_tt'])
        # setup utc time checkbox
        self.utc_checkbox = QCheckBox(main.lang['utc_checkbox'], self)
        self.utc_checkbox.setChecked(main._utc)
        self.utc_checkbox.setToolTip(main.lang['utc_checkbox_tt'])
        self.utc_checkbox.stateChanged.connect(self._utc_changed)
        # setup interval label
        self.timer_label = QLabel(self.lang['timer_label'], self)
        self.timer_label.setToolTip(self.lang['timer_label_tt'])
        # setup interval spinbox
        self.timer_spinbox = QSpinBox(self)
        self.timer_spinbox.setToolTip(self.lang['timer_spinbox_tt'])
        self.timer_spinbox.setMinimum(1)
        self.timer_spinbox.setMaximum(86400000)
        self.timer_spinbox.setValue(self.main._msec)
        self.timer_spinbox.valueChanged.connect(self._timer_change)
        # setup add button
        self.add_button = QPushButton(main.lang['add_button'], self)
        self.add_button.setToolTip(main.lang['add_button_tt'])
        self.add_button.clicked.connect(self._add_time)
        # setup del button
        self.del_button = QPushButton(main.lang['del_button'], self)
        self.del_button.setToolTip(main.lang['del_button_tt'])
        self.del_button.clicked.connect(self._del_time)
        # setup close button
        self.close_button = QPushButton(main.lang['close_button'], self)
        self.close_button.setToolTip(main.lang['close_button_tt'])
        self.close_button.clicked.connect(self.close)
        # setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timeout)
        self.timer.start(self.main._msec)
        # setup time h box layout
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.time_label)
        self.h_box.addWidget(self.utc_checkbox)
        # setup timer h box layout
        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.timer_label)
        self.h_box2.addWidget(self.timer_spinbox)
        # setup v box layout
        self.v_box = QVBoxLayout(self)
        self.v_box.addWidget(self.list)
        self.v_box.addLayout(self.h_box)
        self.v_box.addLayout(self.h_box2)
        self.v_box.addWidget(self.add_button)
        self.v_box.addWidget(self.del_button)
        self.v_box.addWidget(self.close_button)
        self.setLayout(self.v_box)
        # show
        self.show()

    @try_except()
    def _timeout(self):
        self.time_label.setText(get_time(self.main._utc))

    @try_except()
    def _list_fill(self):
        self.list.clear()
        for name in self.main.names:
            self.list.addItem(QListWidgetItem(name, self.list))
        self.list.setCurrentRow(0)

    @try_except()
    def _item_double_clicked(self, item):
        self.time_edit = TimeEdit(self, self.list.currentRow())

    @try_except()
    def _utc_changed(self, state):
        self.main._utc = self.utc_checkbox.isChecked()

    @try_except()
    def _timer_change(self, value):
        self.main._msec = value
        self.timer.stop()
        self.main.timer.stop()
        self.timer.start(self.main._msec)
        self.main.timer.start(self.main._msec)

    @try_except()
    def _add_time(self, checked):
        # adding
        name = self.lang['names']
        i = 1
        while name in self.main.names:
            name = self.lang['names'] + ' ' + str(i)
            i += 1
        self.main.times.append('%X')
        self.main.offsets.append((0, 0, 0))
        self.main.names.append(name)
        self.main.colors.append('#000')
        dtime = DTime(self.main, len(self.main.times) - 1)
        dtime.setAccessibleName(self.main.info.NAME)
        dtime._init()
        dtime.resize(100, 100)
        dtime.show()
        self.main.widgets.append(dtime)
        self.main.save_settings()
        self.list.addItem(QListWidgetItem(name, self.list))
        self.list.setCurrentRow(self.list.count() - 1)
        # show success alert
        mbox = QMessageBox(QMessageBox.Information,
                           self.lang['adding_title'],
                           self.lang['adding_text'],
                           QMessageBox.Ok, self)
        mbox.setWindowIcon(QIcon(SUCCESS))
        ok = mbox.button(QMessageBox.Ok)
        ok.setText(self.lang['adding_ok_button'])
        ok.setToolTip(self.lang['adding_ok_button_tt'])
        mbox.exec()

    @try_except()
    def _del_time(self, checked):
        if self.list.count() <= 1:
            return
        # show confirm dialog
        mbox = QMessageBox(QMessageBox.Question, self.lang['delete_title'],
                           self.lang['delete_text'].format(
                               self.list.currentItem().text()),
                           QMessageBox.Yes | QMessageBox.No)
        mbox.setWindowIcon(QIcon(DELETE))
        yes = mbox.button(QMessageBox.Yes)
        yes.setText(self.lang['del_yes_button'])
        yes.setToolTip(self.lang['del_no_button'])
        no = mbox.button(QMessageBox.No)
        no.setText(self.lang['del_no_button'])
        no.setToolTip(self.lang['del_no_button_tt'])
        if mbox.exec() != QMessageBox.Yes:
            return
        # deleting process
        row = self.list.currentRow()
        if row == 0:  # change main win
            self.main.times[0] = self.main.times[1]
            self.main.offsets[0] = self.main.offsets[1]
            self.main.names[0] = self.main.names[1]
            self.main.colors[0] = self.main.colors[1]
            del self.main.times[0]
            del self.main.offsets[0]
            del self.main.names[0]
            del self.main.colors[0]
            size = self.main.sizes[0]
            self.main.resize(size['width'], size['height'])
            self.main.move(size['x'], size['y'])
            self.main.setWindowOpacity(size['opacity'])
            del self.main.sizes[0]
            self.main.widgets[0].destroy()
            del self.main.widgets[0]
            self.main.show()
            self.main._init()
        else:  # remove child win
            del self.main.times[row]
            del self.main.offsets[row]
            del self.main.names[row]
            del self.main.colors[row]
            if row <= len(self.main.sizes):
                del self.main.sizes[row - 1]
            self.main.widgets[row - 1].destroy()
            del self.main.widgets[row - 1]
        self._list_fill()

    @try_except()
    def closeEvent(self, event):
        self.timer.stop()


class TimeEdit(QWidget):
    def __init__(self, settings, element):
        """

        :param settings: Settings object
        :param element: int, index in lists
        """
        # init
        QWidget.__init__(self)
        # setup vars
        self.move_win = None
        self.settings = settings
        self.main = settings.main
        self.element = element
        self.lang = settings.lang
        self.row = settings.list.currentRow()
        if self.element > 0:
            self.widget = self.main.widgets[self.element - 1]
        else:
            self.widget = self.main
        self._palette = self.widget.label.palette()
        # setup window
        self.setWindowIcon(self.main.windowIcon())
        self.setWindowTitle(self.lang['edit_title'])
        self.resize(245, 250)
        # setup time show label
        self.time_show = QLabel(self)
        self.time_show.setAlignment(Qt.AlignCenter)
        font = self.time_show.font()
        font.setPointSize(12)
        font.setBold(True)
        self.time_show.setFont(font)
        self.time_show.setToolTip(self.lang['time_show_tt'])
        # setup hours spinbox
        self.hours = QSpinBox(self)
        self.hours.setMinimum(-23)
        self.hours.setMaximum(23)
        self.hours.setValue(self.main.offsets[element][0])
        self.hours.setToolTip(self.lang['hours_tt'])
        # setup minutes spinbox
        self.minutes = QSpinBox(self)
        self.minutes.setMinimum(-59)
        self.minutes.setMaximum(59)
        self.minutes.setValue(self.main.offsets[element][1])
        self.minutes.setToolTip(self.lang['minutes_tt'])
        # setup seconds spinbox
        self.seconds = QSpinBox(self)
        self.seconds.setMinimum(-59)
        self.seconds.setMaximum(59)
        self.seconds.setValue(self.main.offsets[element][2])
        self.seconds.setToolTip(self.lang['seconds_tt'])
        # setup offset time show label
        self.offset_time = QLabel(self)
        self.offset_time.setAlignment(Qt.AlignCenter)
        self.offset_time.setFont(font)
        self.offset_time.setToolTip(self.lang['offset_time_tt'])
        # setup format label
        self.format_label = QLabel(self.lang['format_label'], self)
        self.format_label.setAlignment(Qt.AlignCenter)
        self.format_label.setToolTip(self.lang['format_label_tt'])
        # setup format edit
        self.format_edit = QLineEdit(self.main.times[element], self)
        self.format_edit.setToolTip(self.lang['format_edit_tt'])
        # setup name edit
        self.name_edit = QLineEdit(self.main.names[element], self)
        self.name_edit.setToolTip(self.lang['name_edit_tt'])
        # setup edit button
        self.edit_button = QPushButton(self.lang['edit_button'], self)
        self.edit_button.setToolTip(self.lang['edit_button_tt'])
        self.edit_button.clicked.connect(self._edit)
        # setup color button
        self.color_button = QPushButton(self.lang['color_button'], self)
        self.color_button.setToolTip(self.lang['color_button_tt'])
        self.color_button.clicked.connect(self._color)
        # setup save button
        self.save_button = QPushButton(self.lang['save_button'], self)
        self.save_button.setToolTip(self.lang['save_button_tt'])
        self.save_button.clicked.connect(self._save)
        # setup cancel button
        self.cancel_button = QPushButton(self.lang['cancel_button'], self)
        self.cancel_button.setToolTip(self.lang['cancel_button_tt'])
        self.cancel_button.clicked.connect(self._cancel)
        # setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timeout)
        self.timer.start(self.main._msec)
        # setup h box layout
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.format_label)
        self.h_box.addWidget(self.format_edit)
        # setup h box layout 2
        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.save_button)
        self.h_box2.addWidget(self.cancel_button)
        # setup grid layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.time_show, 0, 0, 1, 3)
        self.grid.addWidget(self.hours, 1, 0)
        self.grid.addWidget(self.minutes, 1, 1)
        self.grid.addWidget(self.seconds, 1, 2)
        self.grid.addWidget(self.offset_time, 2, 0, 1, 3)
        self.grid.addLayout(self.h_box, 3, 0, 1, 3)
        self.grid.addWidget(self.name_edit, 4, 0, 1, 3)
        self.grid.addWidget(self.edit_button, 5, 0, 1, 3)
        self.grid.addWidget(self.color_button, 6, 0, 1, 3)
        self.grid.addLayout(self.h_box2, 7, 0, 1, 3)
        self.setLayout(self.grid)
        # show
        self._timeout()
        self.show()

    @try_except()
    def _timeout(self):
        strf = self.format_edit.text()
        if not strf_validate(strf):
            strf = '%X'
        self.time_show.setText(get_time(self.main._utc))
        self.offset_time.setText(get_time(self.main._utc, strf,
                                          self.hours.value(),
                                          self.minutes.value(),
                                          self.seconds.value()))

    @try_except()
    def _edit(self, checked):
        self.move_win = Edit(self.widget, self.main.widget_manager)

    @try_except()
    def _color(self, checked):
        palette = self.widget.label.palette()
        palette.setColor(QPalette.WindowText,
                         QColorDialog.getColor(
                             palette.color(QPalette.WindowText), self,
                             self.lang['color_title']
                         ))
        self._palette = palette

    @try_except()
    def _save(self, checked):
        self.main.colors[self.element] = self._palette.color(
            QPalette.WindowText).name()
        self.main.names[self.element] = self.name_edit.text()
        time_format = self.format_edit.text()
        if not strf_validate(time_format):
            time_format = '%X'
        self.main.times[self.element] = time_format
        self.main.offsets[self.element] = (self.hours.value(),
                                           self.minutes.value(),
                                           self.seconds.value())
        self.main.save_settings()
        self.settings._list_fill()
        self.widget._init()
        self.close()

    @try_except()
    def _cancel(self, checked):
        self.close()

    @try_except()
    def closeEvent(self, event):
        self.timer.stop()
