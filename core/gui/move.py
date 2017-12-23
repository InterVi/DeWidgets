"""Move widget window."""
import traceback
from PyQt5.QtWidgets import QLabel, QSpinBox, QPushButton, QSlider, QWidget
from PyQt5.QtCore import QRect, Qt, QPoint, QSize
from PyQt5.QtGui import QIcon
from core.paths import MOVE


class Move(QWidget):
    """move widget window"""
    def __init__(self, window, manager):
        """

        :param window: QWidget
        :param manager: WidgetManager class
        """
        super().__init__()
        # vars
        lang = manager.lang
        self.window = window
        self.manager = manager
        self.x_cord = window.pos().x()
        self.y_cord = window.pos().y()
        self.h_win = window.height()
        self.w_win = window.width()
        self.opacity_win = window.windowOpacity()
        screen = manager.main_gui.app.desktop().screenGeometry()
        # setup window
        self.setWindowTitle(lang['MOVE']['title'].format(window.NAME))
        self.setFixedSize(194, 199)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.setWindowIcon(QIcon(MOVE))
        # setup 'X' label
        self.x_label = QLabel(self)
        self.x_label.setGeometry(QRect(26, 10, 20, 16))
        self.x_label.setAlignment(Qt.AlignCenter)
        self.x_label.setText(lang['MOVE']['x_label'])
        # setup 'Y' label
        self.y_label = QLabel(self)
        self.y_label.setGeometry(QRect(133, 10, 20, 15))
        self.y_label.setAlignment(Qt.AlignCenter)
        self.y_label.setText(lang['MOVE']['y_label'])
        # setup 'Height' label
        self.h_label = QLabel(self)
        self.h_label.setGeometry(QRect(3, 70, 80, 15))
        self.h_label.setAlignment(Qt.AlignCenter)
        self.h_label.setText(lang['MOVE']['h_label'])
        # setup 'Width' label
        self.w_label = QLabel(self)
        self.w_label.setGeometry(QRect(110, 70, 80, 15))
        self.w_label.setAlignment(Qt.AlignCenter)
        self.w_label.setText(lang['MOVE']['w_label'])
        # setup 'Opacity' label
        self.opacity_win_label = QLabel(self)
        self.opacity_win_label.setGeometry(QRect(43, 120, 111, 20))
        self.opacity_win_label.setAlignment(Qt.AlignCenter)
        self.opacity_win_label.setText(lang['MOVE']['opacity_label'])
        # setup 'X' spinbox
        self.x_edit = QSpinBox(self)
        self.x_edit.setGeometry(QRect(3, 30, 80, 27))
        self.x_edit.setToolTip(lang['MOVE']['x_edit_tt'])
        self.x_edit.setMinimum(0)
        self.x_edit.setMaximum(screen.width())
        self.x_edit.setValue(self.x_cord)
        self.x_edit.valueChanged.connect(self._move)
        # setup 'Y' spinbox
        self.y_edit = QSpinBox(self)
        self.y_edit.setGeometry(QRect(110, 30, 80, 27))
        self.y_edit.setToolTip(lang['MOVE']['y_edit_tt'])
        self.y_edit.setMinimum(0)
        self.y_edit.setMaximum(screen.height())
        self.y_edit.setValue(self.y_cord)
        self.y_edit.valueChanged.connect(self._move)
        # setup 'Height' spinbox
        self.h_edit = QSpinBox(self)
        self.h_edit.setGeometry(QRect(3, 90, 80, 27))
        self.h_edit.setToolTip(lang['MOVE']['h_edit_tt'])
        self.h_edit.setMinimum(0)
        self.h_edit.setMaximum(screen.height())
        self.h_edit.setValue(self.h_win)
        self.h_edit.valueChanged.connect(self._resize)
        # setup 'Width' spinbox
        self.w_edit = QSpinBox(self)
        self.w_edit.setGeometry(QRect(110, 90, 80, 27))
        self.w_edit.setToolTip(lang['MOVE']['w_edit_tt'])
        self.w_edit.setMinimum(0)
        self.w_edit.setMaximum(screen.width())
        self.w_edit.setValue(self.w_win)
        self.w_edit.valueChanged.connect(self._resize)
        # setup slider
        self.slider = QSlider(self)
        self.slider.setGeometry(QRect(3, 140, 188, 21))
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setValue(self.opacity_win * 100)
        self.slider.setToolTip(str(self.opacity_win))
        self.slider.valueChanged.connect(self._opacity)
        # setup 'Save' button
        self.save_button = QPushButton(lang['MOVE']['save_button'], self)
        self.save_button.setToolTip(lang['MOVE']['save_button_tt'])
        self.save_button.setGeometry(QRect(3, 170, 94, 27))
        self.save_button.clicked.connect(self._save)
        # setup 'Cancel' button
        self.cancel_button = QPushButton(lang['MOVE']['cancel_button'], self)
        self.cancel_button.setToolTip(lang['MOVE']['cancel_button_tt'])
        self.cancel_button.setGeometry(QRect(97, 170, 94, 27))
        self.cancel_button.clicked.connect(self._cancel)
        # show
        self.show()

    def _save(self):
        try:
            self.manager.edit_mode(False, self.window.NAME)
            self.close()
        except:
            print(traceback.format_exc())

    def _cancel(self):
        try:
            self.window.move(QPoint(self.x_cord, self.y_cord))
            self.window.resize(QSize(self.w_win, self.h_win))
            self.window.setWindowOpacity(self.opacity_win)
            self.close()
        except:
            print(traceback.format_exc())

    def _move(self):
        try:
            if not self.x_edit.text() or not self.y_edit.text():
                return
            x = self.x_edit.value()
            y = self.y_edit.value()
            self.window.move(QPoint(x, y))
            self.window.show()
        except:
            print(traceback.format_exc())

    def _resize(self):
        try:
            if not self.w_edit.text() or not self.h_edit.text():
                return
            w = self.w_edit.value()
            h = self.h_edit.value()
            self.window.resize(QSize(w, h))
            self.window.show()
        except:
            print(traceback.format_exc())

    def _opacity(self):
        try:
            value = float(self.slider.value() / 100)
            self.window.setWindowOpacity(value)
            self.slider.setToolTip(str(value))
        except:
            print(traceback.format_exc())
