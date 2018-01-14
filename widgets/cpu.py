import os
import traceback
from distutils.util import strtobool
import psutil
from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QPushButton
from PyQt5.QtWidgets import QCheckBox, QSpinBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
from core.manager import Widget, WidgetInfo
from core.paths import RES, SETTINGS


class Info(WidgetInfo):
    def __init__(self, lang):
        WidgetInfo.__init__(self, lang)
        self.lang = lang['CPU_INFO']
        self.NAME = 'CPU Info'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'cpu', 'icon.png'))


class Main(Widget, QWidget):
    def __init__(self, widget_manager, info):
        # init
        Widget.__init__(self, widget_manager, info)
        QWidget.__init__(self)
        self.conf = {}
        self.lang = info.lang
        self.settings_win = None
        # setup stylesheet
        with open(os.path.join(RES, 'cpu', 'style.css'), encoding='utf-8'
                  ) as file:
            style = file.read()
            self.setStyleSheet(style)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.setup_ui)
        # setup vars
        self._widgets = []
        self._setup_vars()

    def _setup_vars(self):
        self._update = 1000
        self._round = 3
        self._percpu = False
        self._percent = True
        self._freq = True
        self._labels = True
        self._text = True

    def setup_ui(self):
        try:
            if self.layout():  # clear
                for w in self._widgets:
                    self.layout().removeWidget(w)
                    w.deleteLater()
                self.layout().update()
                self.update()
                self._widgets.clear()
            else:  # setup v box layout
                self.setLayout(QVBoxLayout(self))
                self.layout().setContentsMargins(0, 0, 0, 0)
            # setup elements
            for i in range(psutil.cpu_count() if self._percpu else 1):
                if self._percent:  # percents
                    pc = psutil.cpu_percent(percpu=self._percpu)
                    if self._labels:  # titles
                        text = self.lang['proc']
                        if self._percpu:
                            text = self.lang['core'].format(str(i))
                        label = QLabel(text, self)
                        label.setAlignment(Qt.AlignCenter)
                        self._widgets.append(label)
                        self.layout().addWidget(label)
                    bar = QProgressBar(self)
                    bar.setMinimum(0)
                    bar.setMaximum(100)
                    bar.setValue(int(pc[i]) if self._percpu else int(pc))
                    self._widgets.append(bar)
                    self.layout().addWidget(bar)
                if self._freq:  # freqs
                    pf = psutil.cpu_freq(self._percpu)
                    if self._labels:  # titles
                        text = self.lang['freq']
                        if self._percpu:
                            text = self.lang['core_freq'].format(str(i))
                        label = QLabel(text, self)
                        label.setAlignment(Qt.AlignCenter)
                        self._widgets.append(label)
                        self.layout().addWidget(label)
                    bar = QProgressBar(self)
                    bar.setMinimum(int(pf[i].min) if self._percpu else
                                   int(pf.min))
                    bar.setMaximum(int(pf[i].max) if self._percpu else
                                   int(pf.max))
                    bar.setValue(int(pf[i].current) if self._percpu else
                                 int(pf.current))
                    self._widgets.append(bar)
                    self.layout().addWidget(bar)
                    if self._text:  # text info
                        text = str(round(pf[i].current, self._round)) if\
                            self._percpu else\
                            str(round(pf.current, self._round))
                        label = QLabel(self.lang['freq_text'].format(text))
                        label.setAlignment(Qt.AlignCenter)
                        self._widgets.append(label)
                        self.layout().addWidget(label)
            # set layout
            self.layout().update()
            self.update()
        except:
            print(traceback.format_exc())

    def _load_settings(self):
        try:
            self.conf = self.widget_manager.get_config(self.info.NAME)
            if 'update' in self.conf:
                self._update = int(self.conf['update'])
            if 'round' in self.conf:
                self._round = int(self.conf['round'])
            if 'percpu' in self.conf:
                self._percpu = bool(strtobool(self.conf['percpu']))
            if 'percent' in self.conf:
                self._percent = bool(strtobool(self.conf['percent']))
            if 'freq' in self.conf:
                self._freq = bool(strtobool(self.conf['freq']))
            if 'labels' in self.conf:
                self._labels = bool(strtobool(self.conf['labels']))
            if 'text' in self.conf:
                self._text = bool(strtobool(self.conf['text']))
        except:
            print(traceback.format_exc())

    def save_settings(self):
        try:
            self.conf['update'] = str(self._update)
            self.conf['round'] = str(self._round)
            self.conf['percpu'] = str(self._percpu)
            self.conf['percent'] = str(self._percent)
            self.conf['freq'] = str(self._freq)
            self.conf['labels'] = str(self._labels)
            self.conf['text'] = str(self._text)
        except:
            print(traceback.format_exc())

    def show_settings(self):
        try:
            self.settings_win = Settings(self)
        except:
            print(traceback.format_exc())

    def unload(self):
        if self.isVisible():
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

    def showEvent(self, event):
        try:
            self.setup_ui()
            self.timer.start(self._update)
        except:
            print(traceback.format_exc())

    def hideEvent(self, event):
        try:
            self.timer.stop()
        except:
            print(traceback.format_exc())


class Settings(QWidget):
    def __init__(self, main):
        # init
        QWidget.__init__(self)
        self.main = main
        self.lang = main.lang
        # setup window
        self.setWindowIcon(QIcon(SETTINGS))
        self.setWindowTitle(self.lang['settings_title'])
        self.resize(200, 260)
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
        # setup percpu checkbox
        self.percpu_checkbox = QCheckBox(self.lang['percpu_checkbox'], self)
        self.percpu_checkbox.setToolTip(self.lang['percpu_checkbox_tt'])
        self.percpu_checkbox.setChecked(main._percpu)
        # setup percent checkbox
        self.percent_checkbox = QCheckBox(self.lang['percent_checkbox'], self)
        self.percent_checkbox.setToolTip(self.lang['percent_checkbox_tt'])
        self.percent_checkbox.setChecked(main._percent)
        # setup freq checkbox
        self.freq_checkbox = QCheckBox(self.lang['freq_checkbox'], self)
        self.freq_checkbox.setToolTip(self.lang['freq_checkbox_tt'])
        self.freq_checkbox.setChecked(main._freq)
        # setup labels checkbox
        self.labels_checkbox = QCheckBox(self.lang['labels_checkbox'], self)
        self.labels_checkbox.setToolTip(self.lang['labels_checkbox_tt'])
        self.labels_checkbox.setChecked(main._labels)
        # setup text checkbox
        self.text_checkbox = QCheckBox(self.lang['text_checkbox'], self)
        self.text_checkbox.setToolTip(self.lang['text_checkbox_tt'])
        self.text_checkbox.setChecked(main._text)
        # setup save button
        self.save_button = QPushButton(self.lang['save_button'], self)
        self.save_button.setToolTip(self.lang['save_button_tt'])
        self.save_button.clicked.connect(self._save)
        # setup cancel button
        self.cancel_button = QPushButton(self.lang['cancel_button'], self)
        self.cancel_button.setToolTip(self.lang['cancel_button_tt'])
        self.cancel_button.clicked.connect(self.close)
        # setup h box layout
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.save_button)
        self.h_box.addWidget(self.cancel_button)
        # setup layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.update_label, 0, 0)
        self.grid.addWidget(self.update_spinbox, 0, 1)
        self.grid.addWidget(self.round_label, 1, 0)
        self.grid.addWidget(self.round_spinbox, 1, 1)
        self.grid.addWidget(self.percpu_checkbox, 2, 0, 1, 2)
        self.grid.addWidget(self.percent_checkbox, 3, 0, 1, 2)
        self.grid.addWidget(self.freq_checkbox, 4, 0, 1, 2)
        self.grid.addWidget(self.labels_checkbox, 5, 0, 1, 2)
        self.grid.addWidget(self.text_checkbox, 6, 0, 1, 2)
        self.grid.addLayout(self.h_box, 7, 0, 1, 2)
        self.setLayout(self.grid)
        # show
        self.show()

    def _save(self):
        try:
            self.main._update = self.update_spinbox.value()
            self.main._round = self.round_spinbox.value()
            self.main._percpu = self.percpu_checkbox.isChecked()
            self.main._percent = self.percent_checkbox.isChecked()
            self.main._freq = self.freq_checkbox.isChecked()
            self.main._labels = self.labels_checkbox.isChecked()
            self.main._text = self.text_checkbox.isChecked()
            self.main.save_settings()
            self.main.timer.stop()
            self.main.timer.start(self.main._update)
            self.close()
        except:
            print(traceback.format_exc())
