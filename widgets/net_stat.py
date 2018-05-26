import os
import json
from enum import IntEnum
from distutils.util import strtobool
import psutil
from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QPushButton
from PyQt5.QtWidgets import QCheckBox, QSpinBox, QComboBox, QListView
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QFont
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt, QTimer
from core.api import Widget, WidgetInfo
from core.paths import RES, SETTINGS
from core.utils import try_except


class Rate(IntEnum):
    B = 0
    KIB = 1
    MIB = 2
    GIB = 3
    TIB = 4
    MBIT = 5


def get_rate(b) -> tuple:
    if b > pow(2, 40):
        return b / pow(2, 40), Rate.TIB
    elif b > pow(2, 30):
        return b / pow(2, 30), Rate.GIB
    elif b > pow(2, 20):
        return b / pow(2, 20), Rate.MIB
    elif b > pow(2, 10):
        return b / pow(2, 10), Rate.KIB
    else:
        return b, Rate.B


def get_mbit(b) -> float:
    return b * 8 / pow(10, 6)


def get_bytes_from_mbit(mbit) -> float:
    return mbit * pow(10, 6) / 8


def get_percent(b, max_b) -> int:
    if not max_b:
        return 0
    return int(b / (max_b / 100))


class Info(WidgetInfo):
    def __init__(self, lang):
        WidgetInfo.__init__(self, lang)
        self.lang = lang['NET_STAT']
        self.NAME = 'NET Stat'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'net_stat', 'icon.png'))


class Main(Widget, QWidget):
    def __init__(self, widget_manager, info):
        # init
        Widget.__init__(self, widget_manager, info)
        QWidget.__init__(self)
        self.conf = {}
        self.lang = info.lang
        self.settings_win = None
        # setup layout
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        # setup stylesheet
        with open(os.path.join(RES, 'net_stat', 'style.css'), encoding='utf-8'
                  ) as file:
            style = file.read()
            self.setStyleSheet(style)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.setup_ui)
        # setup vars
        self.stats = psutil.net_if_stats()
        self._widgets = []
        self._setup_vars()

    def _setup_vars(self):
        self._update = 1000
        self._round = 3
        self._labels = True
        self._pername = False
        self._names = [tuple(self.stats.keys())[0]]
        self._bar = True
        self._text = True
        self._srecv = True
        self._ssent = True
        self._trecv = True
        self._tsent = True
        self._precv = False
        self._psent = False
        self._errin = False
        self._errout = False
        self._dropin = False
        self._dropout = False
        self._con = True
        self._kind = 'inet'
        self._mbit = False
        self._old_counters = None
        self._max_recv_speed = 0
        self._max_sent_speed = 0
        self._palette = QPalette()
        self._palette.setColor(QPalette.WindowText, QColor('#000000'))
        self._font = QFont()

    @try_except()
    def setup_ui(self):
        if self._widgets:  # clear
            for w in self._widgets:
                self.layout().removeWidget(w)
                w.deleteLater()
            self._widgets.clear()
        # setup elements
        if not self._labels:
            self._add_label(self.lang['net'])
        counters = psutil.net_io_counters(self._pername)
        speed = False
        if self._old_counters and type(counters) == type(self._old_counters):
            speed = True
        else:
            self._old_counters = counters
        names = self._names if self._pername else [None]
        for name in names:
            if name:
                if name not in counters:
                    return
                if self._labels:
                    self._add_label(self.lang['net_name'].format(name))
            if speed:
                self.__setup_speed(counters, name)
            self.__setup_total(counters, name)
            self.__setup_packets(counters, name)
            self.__setup_errors(counters, name)
            self.__setup_drops(counters, name)
        self.__setup_con()
        # set layout
        self.layout().update()

    def get_rate_locale(self, rate) -> str:
        if rate == Rate.B:
            return self.lang['b']
        elif rate == Rate.KIB:
            return self.lang['kib']
        elif rate == Rate.MIB:
            return self.lang['mib']
        elif rate == Rate.GIB:
            return self.lang['gib']
        elif rate == Rate.TIB:
            return self.lang['tib']
        elif rate == Rate.MBIT:
            return self.lang['mbit']

    def _add_label(self, text):
        label = QLabel(text, self)
        label.setAlignment(Qt.AlignCenter)
        label.setPalette(self._palette)
        label.setFont(self._font)
        self._widgets.append(label)
        self.layout().addWidget(label)

    def _add_rate_label(self, b, loc_str):
        if self._mbit:
            value = get_mbit(b)
            rate = Rate.MBIT
        else:
            value, rate = get_rate(b)
        value = round(value, self._round)
        self._add_label(loc_str.format(count=value,
                                       rate=self.get_rate_locale(rate)))

    def __setup_speed(self, counters, name=None):
        def setup_bar(b, max_b):
            if not self._bar:
                return
            bar = QProgressBar(self)
            bar.setMinimum(0)
            bar.setMaximum(100)
            bar.setValue(get_percent(b, max_b))
            self._widgets.append(bar)
            self.layout().addWidget(bar)

        def get_max_speed() -> float:
            result = 0
            for name in self.stats:
                if self.stats[name].speed > result:
                    result = self.stats[name].speed
            return get_bytes_from_mbit(result)

        def get_speed(speed, name) -> float:
            result = speed
            if name:
                if name in self.stats and self.stats[name].speed:
                    result = get_bytes_from_mbit(self.stats[name].speed)
            else:
                speed2 = get_max_speed()
                if speed2 > speed:
                    result = speed2
            return result

        if name:
            recv_speed = (counters[name].bytes_recv -
                          self._old_counters[name].bytes_recv)
            sent_speed = (counters[name].bytes_sent -
                          self._old_counters[name].bytes_sent)
        else:
            recv_speed = (counters.bytes_recv -
                          self._old_counters.bytes_recv)
            sent_speed = (counters.bytes_sent -
                          self._old_counters.bytes_sent)
        if self._srecv:
            if recv_speed > self._max_recv_speed:
                self._max_recv_speed = recv_speed
            setup_bar(recv_speed, get_speed(self._max_recv_speed, name))
            if self._text:
                self._add_rate_label(recv_speed, self.lang['speed_recv'])
        if self._ssent:
            if sent_speed > self._max_sent_speed:
                self._max_sent_speed = sent_speed
            setup_bar(sent_speed, get_speed(self._max_sent_speed, name))
            if self._text:
                self._add_rate_label(sent_speed, self.lang['speed_sent'])
        self._old_counters = counters

    def __setup_total(self, counters, name=None):
        if self._trecv:
            b = counters[name].bytes_recv if name else counters.bytes_recv
            self._add_rate_label(b, self.lang['total_recv'])
        if self._tsent:
            b = counters[name].bytes_sent if name else counters.bytes_sent
            self._add_rate_label(b, self.lang['total_sent'])

    def __setup_packets(self, counters, name=None):
        if self._precv:
            p = counters[name].packets_recv if name else counters.packets_recv
            self._add_label(self.lang['packets_recv'].format(str(p)))
        if self._psent:
            p = counters[name].packets_sent if name else counters.packets_sent
            self._add_label(self.lang['packets_sent'].format(str(p)))

    def __setup_errors(self, counters, name=None):
        if self._errin:
            e = counters[name].errin if name else counters.errin
            self._add_label(self.lang['errin'].format(str(e)))
        if self._errout:
            e = counters[name].errout if name else counters.errout
            self._add_label(self.lang['errout'].format(str(e)))

    def __setup_drops(self, counters, name=None):
        if self._dropin:
            d = counters[name].dropin if name else counters.dropin
            self._add_label(self.lang['dropin'].format(str(d)))
        if self._dropout:
            d = counters[name].dropout if name else counters.dropout
            self._add_label(self.lang['dropout'].format(str(d)))

    def __setup_con(self):
        if self._con:
            con = str(len(psutil.net_connections(self._kind)))
            self._add_label(self.lang['connections'].format(con))

    def _load_settings(self):
        self.conf = self.widget_manager.get_config(self.info.NAME)
        if 'update' in self.conf:
            self._update = int(self.conf['update'])
        if 'round' in self.conf:
            self._round = int(self.conf['round'])
        if 'labels' in self.conf:
            self._labels = bool(strtobool(self.conf['labels']))
        if 'pername' in self.conf:
            self._pername = bool(strtobool(self.conf['pername']))
        if 'names' in self.conf:
            self._names = json.loads(self.conf['names'])
        if 'bar' in self.conf:
            self._bar = bool(strtobool(self.conf['bar']))
        if 'text' in self.conf:
            self._text = bool(strtobool(self.conf['text']))
        if 'srecv' in self.conf:
            self._srecv = bool(strtobool(self.conf['srecv']))
        if 'ssent' in self.conf:
            self._ssent = bool(strtobool(self.conf['ssent']))
        if 'trecv' in self.conf:
            self._trecv = bool(strtobool(self.conf['trecv']))
        if 'tsent' in self.conf:
            self._tsent = bool(strtobool(self.conf['tsent']))
        if 'precv' in self.conf:
            self._precv = bool(strtobool(self.conf['precv']))
        if 'psent' in self.conf:
            self._psent = bool(strtobool(self.conf['psent']))
        if 'errin' in self.conf:
            self._errin = bool(strtobool(self.conf['errin']))
        if 'errout' in self.conf:
            self._errout = bool(strtobool(self.conf['errout']))
        if 'dropin' in self.conf:
            self._dropin = bool(strtobool(self.conf['dropin']))
        if 'dropout' in self.conf:
            self._dropout = bool(strtobool(self.conf['dropout']))
        if 'con' in self.conf:
            self._con = bool(strtobool(self.conf['con']))
        if 'kind' in self.conf:
            self._kind = self.conf['kind']
        if 'mbit' in self.conf:
            self._mbit = bool(strtobool(self.conf['mbit']))
        if 'color' in self.conf:
            self._palette.setColor(QPalette.WindowText,
                                   QColor(self.conf['color']))
        if 'size' in self.conf:
            self._font.setPointSize(int(self.conf['size']))
        if 'bold' in self.conf:
            self._font.setBold(bool(self.conf['bold']))

    @try_except()
    def save_settings(self):
        self.conf['update'] = str(self._update)
        self.conf['round'] = str(self._round)
        self.conf['labels'] = str(self._labels)
        self.conf['pername'] = str(self._pername)
        self.conf['names'] = json.dumps(self._names)
        self.conf['bar'] = str(self._bar)
        self.conf['text'] = str(self._text)
        self.conf['srecv'] = str(self._srecv)
        self.conf['ssent'] = str(self._ssent)
        self.conf['trecv'] = str(self._trecv)
        self.conf['tsent'] = str(self._tsent)
        self.conf['precv'] = str(self._precv)
        self.conf['psent'] = str(self._psent)
        self.conf['errin'] = str(self._errin)
        self.conf['errout'] = str(self._errout)
        self.conf['dropin'] = str(self._dropin)
        self.conf['dropout'] = str(self._dropout)
        self.conf['con'] = str(self._con)
        self.conf['kind'] = self._kind
        self.conf['mbit'] = str(self._mbit)
        self.conf['color'] = self._palette.color(QPalette.WindowText).name()
        self.conf['size'] = str(self._font.pointSize())
        self.conf['bold'] = str(self._font.bold())

    @try_except()
    def show_settings(self):
        self.settings_win = Settings(self)

    def unload(self):
        self.save_settings()

    def place(self):
        self.resize(200, 200)
        self._load_settings()

    def boot(self):
        self._load_settings()

    def remove(self):
        self.timer.stop()

    def purge(self):
        self.timer.stop()
        self._setup_vars()

    @try_except()
    def showEvent(self, event):
        self.setup_ui()
        self.timer.start(self._update)

    @try_except()
    def hideEvent(self, event):
        self.timer.stop()


class Settings(QWidget):
    def __init__(self, main):
        # init
        QWidget.__init__(self)
        self.main = main
        self.lang = main.lang
        # setup window
        self.setWindowIcon(QIcon(SETTINGS))
        self.setWindowTitle(self.lang['settings_title'])
        self.resize(500, 460)
        # setup vars
        self._palette = QPalette()
        self._palette.setColor(QPalette.WindowText,
                               main._palette.color(QPalette.WindowText))
        # setup update label
        self.update_label = QLabel(self.lang['update_label'], self)
        self.update_label.setToolTip(self.lang['update_label_tt'])
        # setup update spinbox
        self.update_spinbox = QSpinBox(self)
        self.update_spinbox.setToolTip(self.lang['update_spinbox_tt'])
        self.update_spinbox.setMinimum(500)
        self.update_spinbox.setMaximum(86400000)
        self.update_spinbox.setValue(main._update)
        # setup round label
        self.round_label = QLabel(self.lang['round_label'], self)
        self.round_label.setToolTip(self.lang['round_label_tt'])
        # setup round spinbox
        self.round_spinbox = QSpinBox(self)
        self.round_spinbox.setToolTip(self.lang['round_spinbox_tt'])
        self.round_spinbox.setMinimum(1)
        self.round_spinbox.setMaximum(100)
        self.round_spinbox.setValue(main._round)
        # setup font size spinbox
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setToolTip(self.lang['size_spinbox_tt'])
        self.size_spinbox.setMinimum(8)
        self.size_spinbox.setMaximum(80)
        self.size_spinbox.setValue(main._font.pointSize())
        # setup labels checkbox
        self.labels_checkbox = QCheckBox(self.lang['labels_checkbox'], self)
        self.labels_checkbox.setToolTip(self.lang['labels_checkbox_tt'])
        self.labels_checkbox.setChecked(main._labels)
        # setup pername checkbox
        self.pername_checkbox = QCheckBox(self.lang['pername_checkbox'], self)
        self.pername_checkbox.setToolTip(self.lang['pername_checkbox_tt'])
        self.pername_checkbox.setChecked(main._pername)
        # setup bar checkbox
        self.bar_checkbox = QCheckBox(self.lang['bar_checkbox'], self)
        self.bar_checkbox.setToolTip(self.lang['bar_checkbox_tt'])
        self.bar_checkbox.setChecked(main._bar)
        # setup text checkbox
        self.text_checkbox = QCheckBox(self.lang['text_checkbox'], self)
        self.text_checkbox.setToolTip(self.lang['text_checkbox_tt'])
        self.text_checkbox.setChecked(main._text)
        # setup srecv checkbox
        self.srecv_checkbox = QCheckBox(self.lang['srecv_checkbox'], self)
        self.srecv_checkbox.setToolTip(self.lang['srecv_checkbox_tt'])
        self.srecv_checkbox.setChecked(main._srecv)
        # setup ssent checkbox
        self.ssent_checkbox = QCheckBox(self.lang['ssent_checkbox'], self)
        self.ssent_checkbox.setToolTip(self.lang['ssent_checkbox_tt'])
        self.ssent_checkbox.setChecked(main._ssent)
        # setup trecv checkbox
        self.trecv_checkbox = QCheckBox(self.lang['trecv_checkbox'], self)
        self.trecv_checkbox.setToolTip(self.lang['trecv_checkbox_tt'])
        self.trecv_checkbox.setChecked(main._trecv)
        # setup tsent checkbox
        self.tsent_checkbox = QCheckBox(self.lang['tsent_checkbox'], self)
        self.tsent_checkbox.setToolTip(self.lang['tsent_checkbox_tt'])
        self.tsent_checkbox.setChecked(main._tsent)
        # setup precv checkbox
        self.precv_checkbox = QCheckBox(self.lang['precv_checkbox'], self)
        self.precv_checkbox.setToolTip(self.lang['precv_checkbox_tt'])
        self.precv_checkbox.setChecked(main._precv)
        # setup psent checkbox
        self.psent_checkbox = QCheckBox(self.lang['psent_checkbox'], self)
        self.psent_checkbox.setToolTip(self.lang['psent_checkbox_tt'])
        self.psent_checkbox.setChecked(main._psent)
        # setup errin checkbox
        self.errin_checkbox = QCheckBox(self.lang['errin_checkbox'], self)
        self.errin_checkbox.setToolTip(self.lang['errin_checkbox_tt'])
        self.errin_checkbox.setChecked(main._errin)
        # setup errout checkbox
        self.errout_checkbox = QCheckBox(self.lang['errout_checkbox'], self)
        self.errout_checkbox.setToolTip(self.lang['errout_checkbox_tt'])
        self.errout_checkbox.setChecked(main._errout)
        # setup dropin checkbox
        self.dropin_checkbox = QCheckBox(self.lang['dropin_checkbox'], self)
        self.dropin_checkbox.setToolTip(self.lang['dropin_checkbox_tt'])
        self.dropin_checkbox.setChecked(main._dropin)
        # setup dropout checkbox
        self.dropout_checkbox = QCheckBox(self.lang['dropout_checkbox'], self)
        self.dropout_checkbox.setToolTip(self.lang['dropout_checkbox_tt'])
        self.dropout_checkbox.setChecked(main._dropout)
        # setup connection checkbox
        self.con_checkbox = QCheckBox(self.lang['con_checkbox'], self)
        self.con_checkbox.setToolTip(self.lang['con_checkbox_tt'])
        self.con_checkbox.setChecked(main._con)
        # setup bold checkbox
        self.bold_checkbox = QCheckBox(self.lang['bold_checkbox'], self)
        self.bold_checkbox.setToolTip(self.lang['bold_checkbox_tt'])
        self.bold_checkbox.setChecked(main._font.bold())
        # setup kind cbox combobox
        self.kind_cbox = QComboBox(self)
        self.kind_cbox.setToolTip(self.lang['kind_cbox_tt'])
        self.kind_cbox.addItems((
            'inet', 'inet4', 'inet6', 'tcp', 'tcp4', 'tcp6', 'udp', 'udp4',
            'udp6', 'unix', 'all'
        ))
        self.kind_cbox.setCurrentText(main._kind)
        # setup ifaces list view
        self.ifaces_list = QListView(self)
        self.ifaces_list.setToolTip(self.lang['ifaces_list_tt'])
        self.stats = psutil.net_if_stats()
        ifaces_model = QStandardItemModel(len(self.stats), 1)
        i = 0
        for name in self.stats:
            item = QStandardItem(name)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if name in main._names:
                item.setData(Qt.Checked, Qt.CheckStateRole)
            else:
                item.setData(Qt.Unchecked, Qt.CheckStateRole)
            ifaces_model.setItem(i, 0, item)
            i += 1
        self.ifaces_list.setModel(ifaces_model)
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
        self.cancel_button.clicked.connect(self.close)
        # setup font settings h box layout
        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.size_spinbox)
        self.h_box2.addWidget(self.bold_checkbox)
        # setup buttons h box layout
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.save_button)
        self.h_box.addWidget(self.cancel_button)
        # setup layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.update_label, 0, 0)
        self.grid.addWidget(self.update_spinbox, 0, 1)
        self.grid.addWidget(self.round_label, 1, 0)
        self.grid.addWidget(self.round_spinbox, 1, 1)
        self.grid.addWidget(self.labels_checkbox, 2, 0)
        self.grid.addWidget(self.pername_checkbox, 2, 1)
        self.grid.addWidget(self.bar_checkbox, 3, 0)
        self.grid.addWidget(self.text_checkbox, 3, 1)
        self.grid.addWidget(self.srecv_checkbox, 4, 0)
        self.grid.addWidget(self.ssent_checkbox, 4, 1)
        self.grid.addWidget(self.trecv_checkbox, 5, 0)
        self.grid.addWidget(self.tsent_checkbox, 5, 1)
        self.grid.addWidget(self.precv_checkbox, 6, 0)
        self.grid.addWidget(self.psent_checkbox, 6, 1)
        self.grid.addWidget(self.errin_checkbox, 7, 0)
        self.grid.addWidget(self.errout_checkbox, 7, 1)
        self.grid.addWidget(self.dropin_checkbox, 8, 0)
        self.grid.addWidget(self.dropout_checkbox, 8, 1)
        self.grid.addWidget(self.con_checkbox, 9, 0)
        self.grid.addWidget(self.kind_cbox, 10, 0)
        self.grid.addWidget(self.ifaces_list, 10, 1)
        self.grid.addWidget(self.color_button, 11, 0)
        self.grid.addLayout(self.h_box2, 11, 1)
        self.grid.addLayout(self.h_box, 12, 0, 1, 2)
        self.setLayout(self.grid)
        # show
        self.show()

    @try_except()
    def _color(self, checked):
        self._palette.setColor(QPalette.WindowText,
                               QColorDialog.getColor(
                                   self._palette.color(QPalette.WindowText),
                                   self,
                                   self.lang['color_title'])
                               )

    @try_except()
    def _save(self, checked):
        self.main._update = self.update_spinbox.value()
        self.main._round = self.round_spinbox.value()
        self.main._labels = self.labels_checkbox.isChecked()
        self.main._pername = self.pername_checkbox.isChecked()
        self.main._bar = self.bar_checkbox.isChecked()
        self.main._text = self.text_checkbox.isChecked()
        self.main._srecv = self.srecv_checkbox.isChecked()
        self.main._ssent = self.ssent_checkbox.isChecked()
        self.main._trecv = self.trecv_checkbox.isChecked()
        self.main._tsent = self.tsent_checkbox.isChecked()
        self.main._precv = self.precv_checkbox.isChecked()
        self.main._psent = self.psent_checkbox.isChecked()
        self.main._errin = self.errin_checkbox.isChecked()
        self.main._errout = self.errout_checkbox.isChecked()
        self.main._dropin = self.dropin_checkbox.isChecked()
        self.main._dropout = self.dropout_checkbox.isChecked()
        self.main._con = self.con_checkbox.isChecked()
        self.main._kind = self.kind_cbox.currentText()
        self.main._palette = self._palette
        self.main._font.setPointSize(self.size_spinbox.value())
        self.main._font.setBold(self.bold_checkbox.isChecked())
        names = []
        i = 0
        for name in self.stats:
            ind = self.ifaces_list.model().index(i, 0)
            if self.ifaces_list.model().data(ind, Qt.CheckStateRole):
                names.append(name)
            i += 1
        self.main._names = names
        self.main.save_settings()
        self.main.timer.stop()
        self.main.timer.start(self.main._update)
        self.close()
