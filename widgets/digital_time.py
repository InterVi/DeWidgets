import os
import traceback
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QTimer
from core.manager import Widget
from core.paths import RES


class DTime(QWidget):
    def __init__(self, main, index):
        QWidget.__init__(self)
        self.main = main
        self.index = index
        # setup window
        self.setWindowIcon(main.ICON)
        if index > 0:
            self.setWindowFlags(Qt.CustomizeWindowHint |
                                Qt.WindowStaysOnBottomHint | Qt.Tool)
            self.NAME = 'DTime'
        else:
            self.NAME = main.NAME
        # setup label
        self.label = QLabel(self)
        self.label.setText('00:00:00')
        self.label.setAlignment(Qt.AlignCenter)
        # setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        # setup v box layout
        self.v_box = QVBoxLayout(self)
        self.v_box.setContentsMargins(0, 0, 0, 0)
        self.v_box.addWidget(self.label)
        self.setLayout(self.v_box)
        # self.setStyleSheet('background: black; color: white;')

    def _init(self):
        try:
            self.setWindowTitle(str(self.index) + ': ' + self.label.text())
        except:
            print(traceback.format_exc())

    def _update_time(self):
        try:
            pass
        except:
            print(traceback.format_exc())

    def resizeEvent(self, event):
        try:
            h_size = int(self.height() / 2)
            w_size = int(self.width() / 4)
            size = h_size
            if w_size > h_size:
                size = w_size
            font = self.label.font()
            font.setPointSize(int(size / 2))
            font.setBold(True)
            self.label.setFont(font)
        except:
            print(traceback.format_exc())


class Main(Widget, DTime):
    def __init__(self, widget_manager):
        # init
        Widget.__init__(self, widget_manager)
        DTime.__init__(self, self, 0)
        DTime._init(self)
        self.lang = widget_manager.lang['DIGITAL_TIME']
        # setup widget
        self.NAME = 'Digital Time'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'dtime', 'icon.png'))
