"""Module for widgets drag provide."""
from enum import IntEnum
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from core.utils import try_except

_drags = {}
"""Active drag dict. Keys - widget names, values - DragPanel object."""


class Side(IntEnum):
    LEFT = 0
    RIGHT = 1
    TOP = 3
    BOTTOM = 4


class FormMove(QWidget):
    """Provide drag and drop for any location."""
    def __init__(self):
        QWidget.__init__(self)
        self.setMouseTracking(True)
        self.__mouse_pos = None

    @try_except()
    def mouseMoveEvent(self, event):
        if not self.__mouse_pos:
            return
        self.move(event.pos() - self.__mouse_pos + self.pos())

    @try_except()
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.__mouse_pos = event.pos()

    @try_except()
    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.__mouse_pos = None

    @try_except()
    def is_moving(self) -> bool:
        if self.__mouse_pos:
            return True
        return False


class DragPanel(FormMove):
    def __init__(self, mouse_pos, widget, desktop_geometry, manager):
        FormMove.__init__(self)
        self.setFixedSize(20, 20)
        self.setWindowFlags(Qt.CustomizeWindowHint |
                            Qt.WindowStaysOnBottomHint | Qt.Tool)
        self.setWindowTitle('DragPanel')
        self.__old_pos = self.pos()
        self.mouse_pos = mouse_pos
        self.widget = widget
        self.desktop_geometry = desktop_geometry
        self.manager = manager
        self.move(self.get_pos())
        self.show()

    def get_free_side(self) -> set:
        result = []
        left = self.widget.geometry().left()
        right = self.desktop_geometry.width() - self.widget.geometry().right()
        top = self.widget.geometry().top()
        bottom = \
            self.desktop_geometry.height() - self.widget.geometry().bottom()
        if left > 20:
            result.append(left)
        if right > 20:
            result.append(right)
        if top > 20:
            result.append(top)
        if bottom > 20:
            result.append(bottom)
        result.sort()
        for i in range(len(result)):
            if result[i] == left:
                result[i] = Side.LEFT
            elif result[i] == right:
                result[i] = Side.RIGHT
            elif result[i] == top:
                result[i] = Side.TOP
            elif result[i] == bottom:
                result[i] = Side.BOTTOM
        return set(result)

    def get_mouse_sides(self) -> tuple:
        h = Side.LEFT
        v = Side.TOP
        width = self.widget.width()
        height = self.widget.height()
        x = self.mouse_pos.x()
        y = self.mouse_pos.y()
        if x > width / 2:
            h = Side.RIGHT
        if y > height / 2:
            v = Side.BOTTOM
        hp = x if h == Side.LEFT else width - x
        vp = y if v == Side.TOP else height - y
        if hp <= vp:
            return h, v, h, v
        return v, h, h, v

    def get_side(self) -> Side:
        free = self.get_free_side()
        mouse = self.get_mouse_sides()[0]
        if mouse in free:
            return mouse
        return free.pop()

    def get_pos(self) -> QPoint:
        side = self.get_side()
        h, v = self.get_mouse_sides()[-2:]
        wg = self.widget.geometry()
        if side == Side.LEFT:
            if v == Side.TOP:
                return QPoint(wg.left() - 20, wg.top())
            return QPoint(wg.left() - 20, wg.bottom() - 20)
        elif side == Side.RIGHT:
            if v == Side.TOP:
                return QPoint(wg.right() + 1, wg.top())
            return QPoint(wg.right() + 1, wg.bottom() - 20)
        elif side == Side.TOP:
            if h == Side.LEFT:
                return QPoint(wg.left(), wg.top() - 20)
            return QPoint(wg.right() - 20, wg.top() - 20)
        elif side == Side.BOTTOM:
            if h == Side.LEFT:
                return QPoint(wg.left(), wg.bottom() + 1)
            return QPoint(wg.right() - 20, wg.bottom() + 1)

    @try_except()
    def moveEvent(self, event):
        if not self.is_moving():
            return
        self.widget.move(event.pos() - event.oldPos() + self.widget.pos())

    @try_except()
    def leaveEvent(self, event):
        self.close()
        del _drags[self.widget.accessibleName()]
        self.manager.edit_mode(False, self.widget.accessibleName())


def mouse_enter(manager, qwidget):
    """Decorator for enterEvent.

    :param manager: WidgetManager object
    :param qwidget: QWidget
    :return: wrapped function
    """
    def wrapper(func):
        def enter_event(event):
            @try_except()
            def show():
                main_win = manager.main_gui.main
                app = manager.main_gui.app
                if not main_win.edit_mode_checkbox.isChecked():
                    return
                name = qwidget.accessibleName()
                if name in _drags:
                    return
                _drags[name] = DragPanel(
                    event.pos(), qwidget, app.desktop().screenGeometry(),
                    manager
                )

            show()
            return func(event)

        return enter_event

    return wrapper
