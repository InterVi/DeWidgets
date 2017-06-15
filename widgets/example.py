from PyQt5.QtWidgets import QWidget
from core.manager import Widget


class Main(Widget, QWidget):
    def __init__(self, widget_manager):
        Widget.__init__(self, widget_manager)
        QWidget.__init__(self)
        self.NAME = 'Example Widget'
        self.DESCRIPTION = 'This is a example widget.'
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi'
