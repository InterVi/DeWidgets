"""Help windows."""
import traceback
from PyQt5.QtWidgets import QWidget, QTextBrowser, QGridLayout, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from core.paths import HELP, LICENSE, AVA, LICENSE_TXT
from core.utils import try_except


class Help(QWidget):
    """help window"""
    def __init__(self, lang):
        super().__init__()
        self.lang = lang
        self.license_window = None
        self.author_window = None
        # setup window
        self.setWindowTitle(lang['HELP']['title'])
        self.resize(400, 450)
        self.setWindowIcon(QIcon(HELP))
        # setup text
        self.text = QTextBrowser()
        self.text.setOpenExternalLinks(True)
        self.text.setHtml(lang['HELP']['html'])
        # setup 'License' button
        self.license_button = QPushButton(lang['HELP']['license_button'], self)
        self.license_button.setToolTip(lang['HELP']['license_button_tt'])
        self.license_button.clicked.connect(self._show_license)
        # setup 'Author' button
        self.author_button = QPushButton(lang['HELP']['author_button'], self)
        self.author_button.setToolTip(lang['HELP']['author_button_tt'])
        self.author_button.clicked.connect(self._show_author)
        # setup 'Close' button
        self.exit_button = QPushButton(lang['HELP']['exit_button'], self)
        self.exit_button.setToolTip(lang['HELP']['exit_button_tt'])
        self.exit_button.clicked.connect(self.hide)  # close, destroy - bugs
        # setup grid
        self.grid = QGridLayout()
        self.grid.addWidget(self.text, 0, 0, 1, 3)
        self.grid.addWidget(self.license_button, 1, 0)
        self.grid.addWidget(self.author_button, 1, 1)
        self.grid.addWidget(self.exit_button, 1, 2)
        self.setLayout(self.grid)
        # show
        self.show()

    @try_except
    def _show_license(self, checked):
        self.license_window = License(self.lang)

    @try_except
    def _show_author(self, checked):
        self.author_window = Author(self.lang)


class TextViewer(QWidget):
    """view text and close button, base super class"""
    def __init__(self, title, exit, exit_tt):
        super().__init__()
        # setup window
        self.setWindowTitle(title)
        self.resize(400, 400)
        # setup text
        self.text = QTextBrowser()
        self.text.setOpenExternalLinks(True)
        # setup 'Close' button
        self.exit_button = QPushButton(exit, self)
        self.exit_button.setToolTip(exit_tt)
        self.exit_button.clicked.connect(self.hide)  # close, destroy - bugs
        # setup v layout
        self.v_box = QVBoxLayout(self)
        self.v_box.addWidget(self.text)
        self.v_box.addWidget(self.exit_button)
        self.setLayout(self.v_box)


class License(TextViewer):
    """show license window"""
    def __init__(self, lang):
        # init
        super().__init__(lang['LICENSE']['title'],
                         lang['LICENSE']['exit_button'],
                         lang['LICENSE']['exit_button_tt'])
        self.setWindowIcon(QIcon(LICENSE))
        # setup text
        try:
            with open(LICENSE_TXT, 'r', encoding='UTF-8') as text:
                self.text.setText(text.read())
        except:
            print(traceback.format_exc())
        # show
        self.show()


class Author(TextViewer):
    """show author window"""
    def __init__(self, lang):
        # init
        super().__init__(lang['AUTHOR']['title'],
                         lang['AUTHOR']['exit_button'],
                         lang['AUTHOR']['exit_button_tt'])
        self.setWindowIcon(QIcon(AVA))
        # setup image
        self.label_ava = QLabel(self)
        self.label_ava.setAlignment(Qt.AlignCenter)
        try:
            self.label_ava.setPixmap(QPixmap(AVA))
        except:
            print(traceback.format_exc())
        # setup text
        self.text.setText(lang['AUTHOR']['text'])
        # setup v layout
        self.v_box.removeWidget(self.exit_button)
        self.v_box.removeWidget(self.text)
        self.v_box.addWidget(self.label_ava)
        self.v_box.addWidget(self.text)
        self.v_box.addWidget(self.exit_button)
        # show
        self.show()
