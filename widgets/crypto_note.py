import os
import time
import json
import gzip
import base64
import hashlib
import traceback
from distutils.util import strtobool
from Crypto.Cipher import AES
from Crypto import Random
from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QTextEdit, QLineEdit
from PyQt5.QtWidgets import QPushButton, QCheckBox, QMessageBox, QInputDialog
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QRect
from core.manager import Widget, WidgetInfo
from core.paths import RES, SETTINGS, ERROR

ICON_PIXMAP = QPixmap(os.path.join(RES, 'cnote', 'icon.png'))
OPEN_PIXMAP = QPixmap(os.path.join(RES, 'cnote', 'open.png'))


class AESCip:
    # thanks to mnothic, Gregory Goltsov
    # and SquareRootOfTwentyThree from stackowverflow
    """Class for crypt and decrypt text data."""
    def __init__(self, passwd=None, hashpass=None, encoding='utf-8'):
        """Use this constructor or update_pass / update_hash from correct work.

        :param passwd: str, text password
        :param hashpass: str, SHA-256 hex hashed password
        :param encoding: str, default: utf-8
        """
        self.hexpass = None
        """Initial hex hash for get two hash."""
        self.encoding = encoding
        """Text encoding."""
        if passwd:
            self.update_pass(passwd)
        elif hashpass:
            self.update_hash(hashpass)
        else:
            self.__hashpass = None  # using for next operations

    def update_pass(self, passwd):
        """Update hash.

        :param passwd: str, text password
        """
        h = hashlib.sha256()
        h.update(passwd.encode(self.encoding))
        self.update_hash(h.hexdigest())

    def update_hash(self, hashpass):
        """Update hash.

        :param hashpass: str, SHA-256 hex hash password
        """
        self.hexpass = hashpass
        h = hashlib.sha256()
        h.update(hashpass.encode(self.encoding))
        self.__hashpass = h.digest()

    def _pad(self, data) -> bytearray:
        length = AES.block_size - (len(data) % AES.block_size)
        data += bytes([length])*length
        return data

    def _unpad(self, s) -> str:
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, s) -> bytearray:
        """Encrypt text.

        :param s: str for encrypt
        :return: bytearray
        """
        iv = Random.new().read(AES.block_size)
        cip = AES.new(self.__hashpass, AES.MODE_CBC, iv)
        return iv + cip.encrypt(self._pad(gzip.compress(
            s.encode(self.encoding), 9)))

    def decrypt(self, b) -> str:
        """Decrypt text to text.

        :param b: bytearray, encrypted data
        :return: str, decrypted
        """
        cip = AES.new(self.__hashpass, AES.MODE_CBC, b[:AES.block_size])
        return gzip.decompress(self._unpad(
            cip.decrypt(b[AES.block_size:]))).decode('utf-8')


class Info(WidgetInfo):
    def __init__(self, lang):
        WidgetInfo.__init__(self, lang)
        self.lang = lang['CRYPTO_NOTE']
        self.NAME = 'Crypto Note'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'cnote', 'icon.png'))


class Main(Widget, QWidget):
    def __init__(self, widget_manager, info):
        # init
        Widget.__init__(self, widget_manager, info)
        QWidget.__init__(self)
        self.conf = {}
        self.lang = info.lang
        self.note_win = None
        self.settings_win = None
        # setup image
        self.image = QLabel(self)
        self.image.setScaledContents(True)
        self.image.setPixmap(ICON_PIXMAP)
        self.image.mousePressEvent = self._click
        self.image.show()
        # setup timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timeout)
        # setup grid layout
        self.g_box = QGridLayout(self)
        self.g_box.setSpacing(0)
        self.g_box.setContentsMargins(0, 0, 0, 0)
        self.g_box.addWidget(self.image)
        self.setLayout(self.g_box)
        # setup vars
        self._setup_vars()

    def _setup_vars(self):
        self._session = 0
        self._hot_save = True
        self._handing = 100
        self._end_time = 0
        self._pos = None
        self._hexpass = None

    def _timeout(self):
        try:
            if time.time() >= self._end_time:
                if self.note_win:
                    self.note_win._exit()
                else:
                    self._stop_timer()
                    self.image.setPixmap(ICON_PIXMAP)
                    self.image.show()
        except:
            print(traceback.format_exc())

    def _load_settings(self):
        try:
            self.conf = self.widget_manager.get_config(self.info.NAME)
            if 'session' in self.conf:
                self._session = int(self.conf['session'])
            if 'hot_save' in self.conf:
                self._hot_save = bool(strtobool(self.conf['hot_save']))
            if 'handing' in self.conf:
                self._handing = int(self.conf['handing'])
            if 'pos' in self.conf:
                self._pos = QRect(*json.loads(self.conf['pos']))
        except:
            print(traceback.format_exc())

    def save_settings(self):
        try:
            self.conf['session'] = str(self._session)
            self.conf['hot_save'] = str(self._hot_save)
            if self._pos:
                pos = (self._pos.left(), self._pos.top(), self._pos.width(),
                       self._pos.height())
                self.conf['pos'] = json.dumps(pos)
            self.widget_manager.config.save()
        except:
            print(traceback.format_exc())

    def _click(self, event):
        try:
            if self._hexpass:
                self.note_win = Note(self, hexpass=self._hexpass)
            else:
                qid = QInputDialog(self)
                qid.setWindowIcon(QIcon(OPEN_PIXMAP))
                qid.setWindowTitle(self.lang['pass_title'])
                qid.setOkButtonText(self.lang['ok_button'])
                qid.setCancelButtonText(self.lang['pass_cancel_button'])
                if 'note' in self.conf:
                    qid.setLabelText(self.lang['pass_text'])
                    qid.setTextEchoMode(QLineEdit.Password)
                else:
                    qid.setLabelText(self.lang['create_pass_text'])
                if qid.exec() == QInputDialog.Accepted:
                    text = qid.textValue()
                    if text:
                        self.note_win = Note(self, text)
                        if self._session:
                            self._hexpass = self.note_win.cip.hexpass
                            self._start_timer()
                    else:
                        self.show_pass_error(True)
        except:
            print(traceback.format_exc())

    def _stop_timer(self):
        try:
            self.timer.stop()
            self._hexpass = None
        except:
            print(traceback.format_exc())

    def _start_timer(self):
        try:
            self._end_time = time.time() + self._session
            self.timer.start(self._handing)
        except:
            print(traceback.format_exc())

    def show_pass_error(self, empty=False):
        try:
            t = self.lang['empty_text'] if empty else self.lang['wrong_text']
            mbox = QMessageBox(QMessageBox.Critical,
                               self.lang['wrong_title'], t, QMessageBox.Ok,
                               self)
            mbox.setWindowIcon(QIcon(ERROR))
            ok = mbox.button(QMessageBox.Ok)
            ok.setText(self.lang['wrong_ok_button'])
            ok.setToolTip(self.lang['wrong_ok_button_tt'])
            mbox.exec()
        except:
            print(traceback.format_exc())

    def close_note(self):
        try:
            self.note_win = None
        except:
            print(traceback.format_exc())

    def show_settings(self):
        try:
            self.settings_win = Settings(self)
        except:
            print(traceback.format_exc())

    def unload(self):
        self.save_settings()

    def place(self):
        self._load_settings()

    def boot(self):
        self._load_settings()

    def remove(self):
        self._stop_timer()

    def purge(self):
        try:
            self._setup_vars()
            self.remove()
        except:
            print(traceback.format_exc())


class Note(QWidget):
    def __init__(self, main, password=None, hexpass=None):
        """

        :param main: Main object
        :param password: str, raw text password
        :param hexpass: str, sha256 hex from text password
        """
        # init
        QWidget.__init__(self)
        self.main = main
        self.lang = main.lang
        # setup window
        self.setWindowTitle(self.lang['note_title'])
        self.setWindowIcon(QIcon(OPEN_PIXMAP))
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |
                            Qt.WindowFullscreenButtonHint)
        self.resize(500, 500)
        if main._pos:
            self.setGeometry(main._pos)
        # setup warn label
        self.warn_label = QLabel(self)
        self.warn_label.setText(self.lang['warn_label'])
        self.warn_label.setToolTip(self.lang['warn_label_tt'])
        self.warn_label.setAlignment(Qt.AlignCenter)
        # setup text edit
        self.text_edit = QTextEdit(self)
        self.text_edit.textChanged.connect(self._text_changed)
        # setup exit button
        self.exit_button = QPushButton(self.lang['exit_button'], self)
        self.exit_button.setToolTip(self.lang['exit_button_tt'])
        self.exit_button.clicked.connect(self._exit)
        # setup close button
        self.close_button = QPushButton(self.lang['close_button'], self)
        self.close_button.setToolTip(self.lang['close_button_tt'])
        self.close_button.clicked.connect(self._close)
        # setup layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.warn_label, 0, 0, 1, 2)
        self.grid.addWidget(self.text_edit, 1, 0, 1, 2)
        self.grid.addWidget(self.exit_button, 2, 0)
        self.grid.addWidget(self.close_button, 2, 1)
        self.setLayout(self.grid)
        # setup cipher
        self.cip = AESCip(password, hexpass)
        # load note and show
        self._load_note()

    def _text_changed(self):
        try:
            if self.main._hot_save:
                self._save_note()
        except:
            print(traceback.format_exc())

    def _load_note(self):
        try:
            if 'note' in self.main.conf:
                # base64 -> gzip -> AES-256 -> gzip -> text
                note = gzip.decompress(base64.b64decode(self.main.conf['note'])
                                       )
                self.text_edit.setPlainText(self.cip.decrypt(note))
            self.main.image.setPixmap(OPEN_PIXMAP)
            self.main.image.show()
            self.show()
        except:
            print(traceback.format_exc())
            self.cip.hexpass = None
            self.main.show_pass_error()
            self._exit()

    def _save_note(self):
        try:
            # text -> gzip -> AES-256 -> gzip -> base64
            note = base64.b64encode(gzip.compress(self.cip.encrypt(
                self.text_edit.toPlainText()), 9)).decode('ASCII')
            self.main.conf['note'] = note
            self.main.widget_manager.config.save()
        except:
            print(traceback.format_exc())

    def _exit(self):
        try:
            self.main._stop_timer()
            self.main.image.setPixmap(ICON_PIXMAP)
            self.main.image.show()
            self._close()
        except:
            print(traceback.format_exc())

    def _close(self):
        try:
            if self.text_edit.toPlainText():
                self._save_note()
            self.hide()
            if not self.main._session:
                self.main.image.setPixmap(ICON_PIXMAP)
                self.main.image.show()
            self.main.close_note()
        except:
            print(traceback.format_exc())

    def closeEvent(self, event):
        try:
            event.ignore()
            self._close()
        except:
            print(traceback.format_exc())

    def resizeEvent(self, event):
        self.main._pos = self.geometry()

    def moveEvent(self, event):
        self.main._pos = self.geometry()


class Settings(QWidget):
    def __init__(self, main):
        """

        :param main: Main object
        """
        # init
        QWidget.__init__(self)
        self.main = main
        self.lang = main.lang
        # setup window
        self.setWindowTitle(self.lang['settings_title'])
        self.setWindowIcon(QIcon(SETTINGS))
        self.resize(200, 220)
        # setup session label
        self.session_label = QLabel(self.lang['session_label'], self)
        self.session_label.setToolTip(self.lang['session_label_tt'])
        self.session_label.setAlignment(Qt.AlignCenter)
        # setup session spin box
        self.session_sbox = QSpinBox(self)
        self.session_sbox.setToolTip(self.lang['session_sbox_tt'])
        self.session_sbox.setMinimum(0)
        self.session_sbox.setMaximum(3600)
        self.session_sbox.setValue(self.main._session)
        # setup hot save chbox
        self.hot_save = QCheckBox(self.lang['hot_save'], self)
        self.hot_save.setToolTip(self.lang['hot_save_tt'])
        self.hot_save.setChecked(self.main._hot_save)
        # setup change pass label
        self.change_pass = QLabel(self.lang['change_pass'], self)
        self.change_pass.setAlignment(Qt.AlignCenter)
        # setup old pass edit
        self.old_pass = QLineEdit(self)
        self.old_pass.setToolTip(self.lang['old_pass_tt'])
        self.old_pass.setAlignment(Qt.AlignCenter)
        self.old_pass.setEchoMode(QLineEdit.Password)
        # setup new pass edit
        self.new_pass = QLineEdit(self)
        self.new_pass.setToolTip(self.lang['new_pass_tt'])
        self.new_pass.setAlignment(Qt.AlignCenter)
        self.new_pass.setEchoMode(QLineEdit.Password)
        # setup repeat pass edit
        self.rep_pass = QLineEdit(self)
        self.rep_pass.setToolTip(self.lang['rep_pass_tt'])
        self.rep_pass.setAlignment(Qt.AlignCenter)
        self.rep_pass.setEchoMode(QLineEdit.Password)
        # setup enabled
        if 'note' not in self.main.conf:
            self.old_pass.setEnabled(False)
            self.new_pass.setEnabled(False)
            self.rep_pass.setEnabled(False)
        # setup show pass checkbox
        self.show_pass = QCheckBox(self.lang['show_pass'], self)
        self.show_pass.setToolTip(self.lang['show_pass_tt'])
        self.show_pass.stateChanged.connect(self._show_pass)
        # setup save button
        self.save_button = QPushButton(self.lang['save_button'], self)
        self.save_button.setToolTip(self.lang['save_button_tt'])
        self.save_button.clicked.connect(self._save)
        # setup cancel button
        self.cancel_button = QPushButton(self.lang['cancel_button'], self)
        self.cancel_button.setToolTip(self.lang['cancel_button_tt'])
        self.cancel_button.clicked.connect(self.close)
        # setup pass h box layout
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.new_pass)
        self.h_box.addWidget(self.rep_pass)
        # setup buttons h box layout
        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.save_button)
        self.h_box2.addWidget(self.cancel_button)
        # setup grid layout
        self.grid = QGridLayout(self)
        self.grid.addWidget(self.session_label, 0, 0)
        self.grid.addWidget(self.session_sbox, 0, 1)
        self.grid.addWidget(self.hot_save, 1, 0, 1, 2)
        self.grid.addWidget(self.change_pass, 2, 0, 1, 2)
        self.grid.addWidget(self.old_pass, 3, 0, 1, 2)
        self.grid.addLayout(self.h_box, 4, 0, 1, 2)
        self.grid.addWidget(self.show_pass, 5, 0, 1, 2)
        self.grid.addLayout(self.h_box2, 6, 0, 1, 2)
        self.setLayout(self.grid)
        # show
        self.show()

    def _show_pass(self):
        try:
            if self.show_pass.isChecked():
                self.old_pass.setEchoMode(QLineEdit.Normal)
                self.new_pass.setEchoMode(QLineEdit.Normal)
                self.rep_pass.setEchoMode(QLineEdit.Normal)
            else:
                self.old_pass.setEchoMode(QLineEdit.Password)
                self.new_pass.setEchoMode(QLineEdit.Password)
                self.rep_pass.setEchoMode(QLineEdit.Password)
        except:
            print(traceback.format_exc())

    def _save(self):
        try:
            self.main._session = self.session_sbox.value()
            self.main._hot_save = self.hot_save.isChecked()
            if 'note' in self.main.conf:
                # text edit checks
                if self.new_pass.text() != self.rep_pass.text():
                    mbox = QMessageBox(QMessageBox.Critical,
                                       self.lang['disagree_title'],
                                       self.lang['disagree_text'],
                                       QMessageBox.Ok, self)
                    mbox.setWindowIcon(QIcon(ERROR))
                    ok = mbox.button(QMessageBox.Ok)
                    ok.setText(self.lang['dis_ok_button'])
                    ok.setToolTip(self.lang['dis_ok_button_tt'])
                    mbox.exec()
                    return
                elif self.old_pass.text() and (not self.new_pass.text()
                                               or not self.rep_pass.text()):
                    self.main.show_pass_error(True)
                    return
                elif not self.old_pass.text() and (self.new_pass.text()
                                                   or self.rep_pass.text()):
                    self.main.show_pass_error(True)
                    return
                else:
                    try:  # replacing note content
                        cip = AESCip(self.old_pass.text())
                        # base64 -> gzip -> AES-256 -> gzip -> text
                        note = gzip.decompress(base64.b64decode(
                            self.main.conf['note']))
                        note = cip.decrypt(note)
                        cip.update_pass(self.new_pass.text())
                        # text -> gzip -> AES-256 -> gzip -> base64
                        note = base64.b64encode(gzip.compress(
                            cip.encrypt(note), 9)).decode('ASCII')
                        self.main.conf['note'] = note
                    except:  # if bad password (possible)
                        print(traceback.format_exc())
                        self.main.show_pass_error()
                        return
                self.main.save_settings()
            self.close()
        except:
            print(traceback.format_exc())
