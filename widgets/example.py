import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon
from core.manager import Widget
from core.paths import RES

not_loading = True


class Main(Widget, QWidget):
    def __init__(self, widget_manager):
        # init
        Widget.__init__(self, widget_manager)
        QWidget.__init__(self)
        self.lang = widget_manager.lang['EXAMPLE']
        # setup widget
        self.NAME = 'Example Widget'
        self.VERSION = '1.0'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'example', 'icon.png'))
