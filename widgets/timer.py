import os
import time
import math
import json
from distutils.util import strtobool
from PyQt5.QtWidgets import QWidget, QLCDNumber, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QListWidget, QSpinBox, QPushButton, QMenu
from PyQt5.QtWidgets import QCheckBox, QSlider, QMessageBox, QSystemTrayIcon
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from core.api import Widget, WidgetInfo
from core.paths import RES, SETTINGS, PLAY, PAUSE, STOP, SUCCESS
from core.utils import try_except


class Info(WidgetInfo):
    def __init__(self, lang):
        WidgetInfo.__init__(self, lang)
        self.lang = lang['TIMER']
        self.NAME = 'Timer'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'timer', 'icon.png'))


class Main(Widget, QWidget):
    def __init__(self, widget_manager, info):
        # init
        Widget.__init__(self, widget_manager, info)
        QWidget.__init__(self)
        self.conf = {}
        self.lang = info.lang
        self.settings_win = None
        # setup window
        with open(os.path.join(RES, 'timer', 'style.css'),
                  encoding='utf-8') as file:
            self.setStyleSheet(file.read())
        # setup menu
        self.menu = QMenu(self)
        start_action = self.menu.addAction(QIcon(PLAY), self.lang['start'])
        start_action.triggered.connect(self._start)
        pause_action = self.menu.addAction(QIcon(PAUSE), self.lang['pause'])
        pause_action.triggered.connect(self._pause)
        reset_action = self.menu.addAction(QIcon(STOP), self.lang['reset'])
        reset_action.triggered.connect(self._reset)
        # all setups
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._last = 0
        self.list = []
        self.shows = {}
        self.v_box = QVBoxLayout(self)
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.setSpacing(1)
        self.setLayout(self.v_box)
        # constants
        self.TICK = os.path.join(RES, 'timer', 'tick.ogg')
        self.TACK = os.path.join(RES, 'timer', 'tack.ogg')
        self.ALARM = os.path.join(RES, 'timer', 'alarm.ogg')

    @try_except()
    def _add_timer(self, h=0, m=0, s=0, enabled=True):
        lcd = QLCDNumber(self), QLCDNumber(self), QLCDNumber(self)
        for i in range(3):
            lcd[i].display((h, m, s)[i])
            lcd[i].setDigitCount(2)
            lcd[i].setSegmentStyle(QLCDNumber.Flat)
            lcd[i].setEnabled(enabled)
        h_box = QHBoxLayout()
        h_box.setContentsMargins(0, 0, 0, 0)
        h_box.setSpacing(0)
        h_box.addWidget(lcd[0])
        h_box.addWidget(lcd[1])
        h_box.addWidget(lcd[2])
        self.v_box.addLayout(h_box)
        # ------ 0 ------------ 1 -------- 2 -------- 3 -------- 4 ---
        # (lcd, lcd, lcd), QHBoxLayout, is past, is enabled, (h, m, s)
        self.list.append((lcd, h_box, True, enabled, (h, m, s)))

    def _delete_timer(self, index):
        self.v_box.removeItem(self.list[index][1])
        del self.list[index]
        self._reset()  # render bug not fixed :(

    @try_except()
    def _turn_enabled(self, index, enabled):
        item = self.list[index]
        for lcd in item[0]:
            lcd.setEnabled(enabled)
        self.list[index] = item[0], item[1], item[2], enabled, item[4]

    @try_except()
    def _tick(self):
        ticked = False
        sec = math.floor(time.time() - self._last)  # amplify precision
        if not sec:
            return
        for n in range(len(self.list)):
            item = self.list[n]
            if not item[3]:
                continue
            for i in range(int(sec)):
                if not item[0][2].value():
                    if item[0][1].value() or item[0][0].value():
                        item[0][2].display(59)
                        if item[0][1].value():
                            item[0][1].display(item[0][1].value() - 1)
                        else:
                            item[0][1].display(59)
                            item[0][0].display(item[0][0].value() - 1)
                else:
                    item[0][2].display(item[0][2].value() - 1)
                if not item[0][2].value() and not item[0][1].value() \
                        and not item[0][0].value() and item[2]:
                    self._alarm(n)
                    self.list[n] = item[0], item[1], False, item[3], item[4]
                else:
                    ticked = True
        if ticked:
            self._last += 1  # amplify precision
            self._sec_sound()
        else:
            self.timer.stop()

    @try_except()
    def _play(self, file, volume):  # strange, big memory leak and crash
        player = QMediaPlayer(self)
        player.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
        player.setVolume(volume)
        player.play()

    @try_except()
    def _sec_sound(self):
        if not strtobool(self.conf['seconds']):
            return
        volume = int(self.conf['seconds_volume'])
        if int(math.floor(time.time())) % 2 == 0:
            self._play(self.TICK, volume)
        else:
            self._play(self.TACK, volume)

    @try_except()
    def _alarm(self, index):
        if strtobool(self.conf['alarm']):
            self._play(self.ALARM, int(self.conf['alarm_volume']))
        if strtobool(self.conf['alert']):
            self._show_timeout(index)
        if strtobool(self.conf['notify']):
            self.widget_manager.main_gui.main.tray.showMessage(
                self.lang['notify_title'],
                self.lang['notify_mess'].format(self.get_timer_text(index)),
                QSystemTrayIcon.Information, int(self.conf['notify_msec'])
            )

    @try_except()
    def _show_timeout(self, index):
        if index in self.shows:
            return
        self.shows[index] = Timeout(self, self.get_timer_text(index), index)

    @try_except()
    def _start(self, checked):
        self._last = time.time()
        self.timer.start(int(self.conf['tick_ms']))  # amplify precision

    @try_except()
    def _pause(self, checked):
        self.timer.stop()

    @try_except()
    def _reset(self, checked=False):
        self.timer.stop()
        for timer in self.list:
            self.v_box.removeItem(timer[1])
        self._save_timers()
        self.list.clear()
        self._load_timers()
        self.layout().update()

    def _load_timers(self):
        if ('timers' not in self.conf) or self.conf['timers'] == '[]' or \
                not self.conf['timers']:
            self._add_timer()
            return
        for data in json.loads(self.conf['timers']):
            self._add_timer(*data)

    def _save_timers(self):
        if not self.conf:
            return
        timers = []
        for timer in self.list:
            timers.append((timer[4][0], timer[4][1], timer[4][2], timer[3]))
        self.conf['timers'] = json.dumps(timers)

    def _setup_conf(self):
        self.conf = self.widget_manager.get_config(self.info.NAME)
        if 'alarm' not in self.conf:
            self.conf['alarm'] = 'True'
        if 'alert' not in self.conf:
            self.conf['alert'] = 'True'
        if 'notify' not in self.conf:
            self.conf['notify'] = 'True'
        if 'notify_msec' not in self.conf:
            self.conf['notify_msec'] = str(10000)
        if 'seconds' not in self.conf:
            self.conf['seconds'] = 'False'
        if 'alarm_volume' not in self.conf:
            self.conf['alarm_volume'] = str(100)
        if 'seconds_volume' not in self.conf:
            self.conf['seconds_volume'] = str(100)
        if 'tick_ms' not in self.conf:
            self.conf['tick_ms'] = str(10)

    def place(self):
        self._setup_conf()
        self._load_timers()

    def boot(self):
        self._setup_conf()
        self._load_timers()

    def unload(self):
        self._save_timers()

    @try_except()
    def show_settings(self):
        self.settings_win = Settings(self)

    @try_except()
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.menu.exec(event.globalPos())

    @try_except()
    def mouseDoubleClickEvent(self, event):
        index = int(event.pos().y()/(self.height()/(len(self.list))))
        self._turn_enabled(index, not self.list[index][3])

    def get_timer_text(self, index) -> str:
        timer = str(self.list[index][4][0]) + ':'
        timer += str(self.list[index][4][1]) + ':'
        timer += str(self.list[index][4][2])
        return timer


class Timeout(QMessageBox):
    def __init__(self, main, timer, index):
        QMessageBox.__init__(self)
        QMessageBox.__init__(self, QMessageBox.Information,
                             main.lang['success_title'],
                             main.lang['success_text'].format(timer),
                             QMessageBox.NoButton, main)
        self.main = main
        self.index = index
        # setup window
        self.setStandardButtons(QMessageBox.NoButton)
        self.setWindowIcon(QIcon(SUCCESS))
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |
                            Qt.WindowStaysOnTopHint | Qt.Tool)
        # setup 'Ok' button
        ok = QPushButton(main.lang['success_ok_button'], self)
        ok.setToolTip(main.lang['success_ok_button_tt'])
        ok.clicked.connect(self._exit)
        self.layout().addWidget(ok)
        # show
        self.show()

    @try_except()
    def _exit(self, checked):
        del self.main.shows[self.index]
        self.deleteLater()


class Settings(QWidget):
    def __init__(self, main):
        self.main = main
        QWidget.__init__(self)
        self.ts_win = None
        # setup window
        self.setWindowIcon(QIcon(SETTINGS))
        self.setWindowTitle(main.lang['settings_title'])
        self.resize(300, 400)
        # setup list
        self.list = QListWidget(self)
        self.list.setToolTip(main.lang['list_tt'])
        self.list.itemClicked.connect(self._change_enabled)
        self.list.itemDoubleClicked.connect(self._item_double_clicked)
        self._list_fill()
        # setup 'Alert' checkbox
        self.alert_checkbox = QCheckBox(main.lang['alert_checkbox'], self)
        self.alert_checkbox.setToolTip(main.lang['alert_checkbox_tt'])
        self.alert_checkbox.stateChanged.connect(self._alert_checkbox_changed)
        if 'alert' in main.conf:
            self.alert_checkbox.setChecked(bool(strtobool(main.conf['alert'])))
        # setup 'Notify' checkbox
        self.notify_checkbox = QCheckBox(main.lang['notify_checkbox'], self)
        self.notify_checkbox.setToolTip(main.lang['notify_checkbox_tt'])
        self.notify_checkbox.stateChanged.connect(
            self._notify_checkbox_changed)
        if 'notify' in main.conf:
            self.notify_checkbox.setChecked(bool(strtobool(
                main.conf['notify'])))
        # setup 'Alarm' checkbox
        self.alarm_checkbox = QCheckBox(main.lang['alarm_checkbox'], self)
        self.alarm_checkbox.setToolTip(main.lang['alarm_checkbox_tt'])
        self.alarm_checkbox.stateChanged.connect(self._alarm_checkbox_changed)
        if 'alarm' in main.conf:
            self.alarm_checkbox.setChecked(bool(strtobool(main.conf['alarm'])))
        # setup 'Seconds' checkbox
        self.seconds_checkbox = QCheckBox(main.lang['seconds_checkbox'], self)
        self.seconds_checkbox.setToolTip(main.lang['seconds_checkbox_tt'])
        self.seconds_checkbox.stateChanged.connect(
            self._seconds_checkbox_changed)
        if 'seconds' in main.conf:
            self.seconds_checkbox.setChecked(bool(strtobool(
                main.conf['seconds'])))
        # setup 'Alarm volume' slider
        self.alarm_slider = QSlider(Qt.Horizontal, self)
        self.alarm_slider.setToolTip(main.lang['alarm_slider_tt'])
        self.alarm_slider.valueChanged.connect(self._alarm_volume_changed)
        if 'alarm_volume' in main.conf:
            self.alarm_slider.setValue(int(main.conf['alarm_volume']))
        # setup 'Seconds volume' slider
        self.seconds_slider = QSlider(Qt.Horizontal, self)
        self.seconds_slider.setToolTip(main.lang['seconds_slider_tt'])
        self.seconds_slider.valueChanged.connect(self._seconds_volume_changed)
        if 'seconds_volume' in main.conf:
            self.seconds_slider.setValue(int(main.conf['seconds_volume']))
        # setup 'Notify time' spinbox
        self.notify_time = QSpinBox(self)
        self.notify_time.setToolTip(main.lang['notify_time_tt'])
        self.notify_time.valueChanged.connect(self._time_changed)
        if 'notify_msec' in main.conf and\
                        int(main.conf['notify_msec']) >= 1000:
            self.notify_time.setValue(int(int(main.conf['notify_msec'])/1000))
        else:
            self.notify_time.setValue(10)
        # setup 'Tick' label
        self.tick_label = QLabel(main.lang['tick_label'], self)
        # setup 'Tick ms' spinbox
        self.tick_ms = QSpinBox(self)
        self.tick_ms.setToolTip(main.lang['tick_ms_tt'])
        self.tick_ms.valueChanged.connect(self._tick_changed)
        if 'tick_ms' in main.conf:
            self.tick_ms.setValue(int(main.conf['tick_ms']))
        # setup 'Add' button
        self.add_button = QPushButton(main.lang['add_button'], self)
        self.add_button.setToolTip(main.lang['add_button_tt'])
        self.add_button.clicked.connect(self._add)
        # setup 'Delete' button
        self.delete_button = QPushButton(main.lang['delete_button'], self)
        self.delete_button.setToolTip(main.lang['delete_button_tt'])
        self.delete_button.clicked.connect(self._delete)
        # setup 'Close' button
        self.close_button = QPushButton(main.lang['close_button'], self)
        self.close_button.setToolTip(main.lang['close_button_tt'])
        self.close_button.clicked.connect(self.close)
        # setup alarm h box layout
        self.h_box1 = QHBoxLayout()
        self.h_box1.addWidget(self.alarm_checkbox)
        self.h_box1.addWidget(self.alarm_slider)
        # setup seconds h box layout
        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.seconds_checkbox)
        self.h_box2.addWidget(self.seconds_slider)
        # setup notify h box layout
        self.h_box3 = QHBoxLayout()
        self.h_box3.addWidget(self.notify_checkbox)
        self.h_box3.addWidget(self.notify_time)
        # setup tick h box layout
        self.h_box4 = QHBoxLayout()
        self.h_box4.addWidget(self.tick_label)
        self.h_box4.addWidget(self.tick_ms)
        # setup v box layout
        self.v_box = QVBoxLayout(self)
        self.v_box.addWidget(self.list)
        self.v_box.addWidget(self.alert_checkbox)
        self.v_box.addLayout(self.h_box3)
        self.v_box.addLayout(self.h_box1)
        self.v_box.addLayout(self.h_box2)
        self.v_box.addLayout(self.h_box4)
        self.v_box.addWidget(self.add_button)
        self.v_box.addWidget(self.delete_button)
        self.v_box.addWidget(self.close_button)
        self.setLayout(self.v_box)
        # show
        self._change_enabled()
        self.show()

    def _change_enabled(self):
        if self.list.currentItem():
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)

    @try_except()
    def _list_fill(self):
        self.list.clear()
        for i in range(len(self.main.list)):
            item = QListWidgetItem(self.main.get_timer_text(i), self.list)
            if self.main.list[i][3]:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self.list.addItem(item)

    @try_except()
    def _item_double_clicked(self, item):
        self.ts_win = TimerSettings(self, True)

    @try_except()
    def _alert_checkbox_changed(self, state):
        self.main.conf['alert'] = str(self.alert_checkbox.isChecked())

    @try_except()
    def _alarm_checkbox_changed(self, state):
        self.main.conf['alarm'] = str(self.alarm_checkbox.isChecked())

    @try_except()
    def _notify_checkbox_changed(self, state):
        self.main.conf['notify'] = str(self.notify_checkbox.isChecked())

    @try_except()
    def _seconds_checkbox_changed(self, state):
        self.main.conf['seconds'] = str(self.seconds_checkbox.isChecked())

    @try_except()
    def _alarm_volume_changed(self, value):
        self.main.conf['alarm_volume'] = str(int(value))

    @try_except()
    def _seconds_volume_changed(self, value):
        self.main.conf['seconds_volume'] = str(int(value))

    @try_except()
    def _time_changed(self, value):
        self.main.conf['notify_msec'] = str(int(value * 1000))

    @try_except()
    def _tick_changed(self, value):
        self.main.conf['tick_ms'] = str(int(value))

    @try_except()
    def _add(self, checked):
        self.ts_win = TimerSettings(self)

    @try_except()
    def _delete(self, checked):
        if self.list.count() <= 1:
            return
        self.main._delete_timer(self.list.currentRow())
        self._list_fill()
        self._change_enabled()


class TimerSettings(QWidget):
    def __init__(self, settings, edit=False):
        QWidget.__init__(self)
        self.settings = settings
        self.index = settings.list.currentRow()
        self.main = settings.main
        self.edit = edit
        # setup window
        if edit:
            timer = settings.list.item(self.index).text()
            self.setWindowTitle(self.main.lang['ts_title'].format(timer))
        else:
            self.setWindowTitle(self.main.lang['ts_title'].format(''))
        self.setWindowIcon(self.main.windowIcon())
        self.resize(210, 120)
        # setup 'Hours' label
        self.h_label = QLabel(self.main.lang['ts_hours'], self)
        # setup 'Minuts' label
        self.m_label = QLabel(self.main.lang['ts_minuts'], self)
        # setup 'Seconds' label
        self.s_label = QLabel(self.main.lang['ts_seconds'], self)
        # setup 'Hours' spinbox
        self.hbox = QSpinBox(self)
        if edit:
            self.hbox.setValue(self.main.list[self.index][4][0])
        # setup 'Minuts' spinbox
        self.mbox = QSpinBox(self)
        if edit:
            self.mbox.setValue(self.main.list[self.index][4][1])
        # setup 'Seconds' spinbox
        self.sbox = QSpinBox(self)
        if edit:
            self.sbox.setValue(self.main.list[self.index][4][2])
        # setup 'Enabled' checkbox
        self.enabled = QCheckBox(self.main.lang['ts_enabled'], self)
        self.enabled.setToolTip(self.main.lang['ts_enabled_tt'])
        if edit:
            self.enabled.setChecked(self.main.list[self.index][3])
        else:
            self.enabled.setChecked(True)
        # setup 'Save' button
        self.save_button = QPushButton(self.main.lang['ts_save_button'], self)
        self.save_button.setToolTip(self.main.lang['ts_save_button_tt'])
        self.save_button.clicked.connect(self._save_exit)
        # setup 'Cancel' button
        self.cancel_button = QPushButton(self.main.lang['ts_cancel_button'],
                                         self)
        self.cancel_button.setToolTip(self.main.lang['ts_cancel_button_tt'])
        self.cancel_button.clicked.connect(self.close)
        # setup h box layout
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.h_label)
        self.h_box.addWidget(self.m_label)
        self.h_box.addWidget(self.s_label)
        # setup h box layout 2
        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.hbox)
        self.h_box2.addWidget(self.mbox)
        self.h_box2.addWidget(self.sbox)
        # setup h box layout 3
        self.h_box3 = QHBoxLayout()
        self.h_box3.addWidget(self.save_button)
        self.h_box3.addWidget(self.cancel_button)
        # setup v box layout
        self.v_box = QVBoxLayout(self)
        self.v_box.addLayout(self.h_box)
        self.v_box.addLayout(self.h_box2)
        self.v_box.addWidget(self.enabled)
        self.v_box.addLayout(self.h_box3)
        self.setLayout(self.v_box)
        # show
        self.show()

    @try_except()
    def _save_exit(self, checked):
        if self.edit:
            item = self.main.list[self.index]
            time_ = self.hbox.value(), self.mbox.value(), self.sbox.value()
            e = self.enabled.isChecked()
            for i in range(3):
                item[0][i].display(time_[i])
                item[0][i].setEnabled(e)
            self.main.list[self.index] = (item[0], item[1], item[2], e,
                                          time_)
            self.settings._list_fill()
            self.settings._change_enabled()
        else:
            self.main._add_timer(self.hbox.value(), self.mbox.value(),
                                 self.sbox.value(),
                                 self.enabled.isChecked())
            self.settings._list_fill()
            self.settings._change_enabled()
        self.close()
