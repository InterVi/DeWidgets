"""Edit widget window."""
from PyQt5.QtWidgets import QLabel, QSpinBox, QPushButton, QSlider, QWidget
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QIcon
from core.paths import MOVE
from core.utils import try_except


class Edit(QWidget):
    """Edit widget window."""
    def __init__(self, window, manager):
        """

        :param window: QWidget
        :param manager: WidgetManager object
        """
        super().__init__()
        # vars
        lang = manager.lang['EDIT']
        self.window = window
        self.manager = manager
        self.x_cord = window.pos().x()
        self.y_cord = window.pos().y()
        self.h_win = window.height()
        self.w_win = window.width()
        self.opacity_win = window.windowOpacity()
        screen = manager.main_gui.app.desktop().screenGeometry()
        # setup window
        self.setWindowTitle(lang['title'].format(window.windowTitle()))
        self.resize(230, 220)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.setWindowIcon(QIcon(MOVE))
        # setup 'X' label
        self.x_label = QLabel(lang['x_label'], self)
        self.x_label.setAlignment(Qt.AlignCenter)
        # setup 'Y' label
        self.y_label = QLabel(lang['y_label'], self)
        self.y_label.setAlignment(Qt.AlignCenter)
        # setup 'Height' label
        self.h_label = QLabel(lang['h_label'], self)
        self.h_label.setAlignment(Qt.AlignCenter)
        # setup 'Width' label
        self.w_label = QLabel(lang['w_label'], self)
        self.w_label.setAlignment(Qt.AlignCenter)
        # setup 'Opacity' label
        self.opacity_win_label = QLabel(lang['opacity_label'], self)
        self.opacity_win_label.setAlignment(Qt.AlignCenter)
        # setup 'X' spinbox
        self.x_edit = QSpinBox(self)
        self.x_edit.setToolTip(lang['x_edit_tt'])
        self.x_edit.setMinimum(0)
        self.x_edit.setMaximum(screen.width())
        self.x_edit.setValue(self.x_cord)
        self.x_edit.valueChanged.connect(self._move)
        # setup 'Y' spinbox
        self.y_edit = QSpinBox(self)
        self.y_edit.setToolTip(lang['y_edit_tt'])
        self.y_edit.setMinimum(0)
        self.y_edit.setMaximum(screen.height())
        self.y_edit.setValue(self.y_cord)
        self.y_edit.valueChanged.connect(self._move)
        # setup 'Height' spinbox
        self.h_edit = QSpinBox(self)
        self.h_edit.setToolTip(lang['h_edit_tt'])
        self.h_edit.setMinimum(0)
        self.h_edit.setMaximum(screen.height())
        self.h_edit.setValue(self.h_win)
        self.h_edit.valueChanged.connect(self._resize)
        # setup 'Width' spinbox
        self.w_edit = QSpinBox(self)
        self.w_edit.setToolTip(lang['w_edit_tt'])
        self.w_edit.setMinimum(0)
        self.w_edit.setMaximum(screen.width())
        self.w_edit.setValue(self.w_win)
        self.w_edit.valueChanged.connect(self._resize)
        # setup opacity slider
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setValue(self.opacity_win * 100)
        self.slider.setToolTip(str(self.opacity_win))
        self.slider.valueChanged.connect(self._opacity)
        # setup 'Save' button
        self.save_button = QPushButton(lang['save_button'], self)
        self.save_button.setToolTip(lang['save_button_tt'])
        self.save_button.clicked.connect(self._save)
        # setup 'Cancel' button
        self.cancel_button = QPushButton(lang['cancel_button'], self)
        self.cancel_button.setToolTip(lang['cancel_button_tt'])
        self.cancel_button.clicked.connect(self._cancel)
        # setup layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.x_label, 0, 0)
        self.grid.addWidget(self.y_label, 0, 1)
        self.grid.addWidget(self.x_edit, 1, 0)
        self.grid.addWidget(self.y_edit, 1, 1)
        self.grid.addWidget(self.h_label, 2, 0)
        self.grid.addWidget(self.w_label, 2, 1)
        self.grid.addWidget(self.h_edit, 3, 0)
        self.grid.addWidget(self.w_edit, 3, 1)
        self.grid.addWidget(self.opacity_win_label, 4, 0, 1, 2)
        self.grid.addWidget(self.slider, 5, 0, 1, 2)
        self.grid.addWidget(self.save_button, 6, 0)
        self.grid.addWidget(self.cancel_button, 6, 1)
        self.setLayout(self.grid)
        # show
        self.show()

    @try_except()
    def _save(self, checked):
        self.manager.edit_mode(False)
        self.close()

    @try_except()
    def _cancel(self, checked):
        self.window.move(QPoint(self.x_cord, self.y_cord))
        self.window.resize(QSize(self.w_win, self.h_win))
        self.window.setWindowOpacity(self.opacity_win)
        self.close()

    @try_except()
    def _move(self, value):
        if not self.x_edit.text() or not self.y_edit.text():
            return
        x = self.x_edit.value()
        y = self.y_edit.value()
        self.window.move(QPoint(x, y))
        self.window.show()

    @try_except()
    def _resize(self, value):
        if not self.w_edit.text() or not self.h_edit.text():
            return
        w = self.w_edit.value()
        h = self.h_edit.value()
        self.window.resize(QSize(w, h))
        self.window.show()

    @try_except()
    def _opacity(self, value):
        value = float(value / 100)
        self.window.setWindowOpacity(value)
        self.slider.setToolTip(str(value))
