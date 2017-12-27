"""Delete widgets GUI."""
import os
import sys
import json
import traceback
from PyQt5.QtWidgets import QWidget, QListWidget, QLabel, QPushButton
from PyQt5.QtWidgets import QMessageBox, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QRect, Qt
from core.paths import CONF_INSTALL, DELETE


class Delete(QWidget):
    def __init__(self, locale, manager):
        """

        :param locale: dict, current locale
        :param manager: WidgetManager class
        """
        # init
        QWidget.__init__(self)
        self.locale = locale
        self.manager = manager
        self.lang = locale['DEL_WIDGETS']
        self.setWindowTitle(self.lang['title'])
        self.setFixedSize(410, 330)
        self.setWindowIcon(QIcon(DELETE))
        # setup widgets list
        self.w_list = QListWidget(self)
        self.w_list.setGeometry(QRect(0, 0, 280, 300))
        self.w_list.setSpacing(2)
        self.w_list.itemClicked.connect(self._list_click)
        self.w_list.itemDoubleClicked.connect(self._list_double_click)
        self._list_fill()
        # setup label
        self.h_label = QLabel(self)
        self.h_label.setGeometry(QRect(0, 305, 410, 17))
        self.h_label.setText(self.lang['label'])
        self.h_label.setAlignment(Qt.AlignCenter)
        # setup delete button
        self.del_button = QPushButton(self.lang['del_button'], self)
        self.del_button.setGeometry(QRect(300, 10, 94, 29))
        self.del_button.setToolTip(self.lang['del_button_tt'])
        self.del_button.clicked.connect(self._delete)
        # setup archives button
        self.arch_button = QPushButton(self.lang['arch_button'], self)
        self.arch_button.setGeometry(QRect(300, 50, 94, 29))
        self.arch_button.setToolTip(self.lang['arch_button_tt'])
        self.arch_button.clicked.connect(self._arch_delete)
        # setup close button
        self.close_button = QPushButton(self.lang['close_button'], self)
        self.close_button.setGeometry(QRect(300, 270, 94, 29))
        self.close_button.setToolTip(self.lang['close_button_tt'])
        self.close_button.clicked.connect(self.close)
        # show
        self.show()

    def _list_fill(self):
        try:
            self.w_list.clear()
            for widget in self.manager.widgets.values():
                try:
                    if widget.NAME not in self.manager.custom_widgets:
                        continue
                    item = QListWidgetItem(self.w_list)
                    item.setIcon(widget.ICON)
                    item.setText(widget.NAME)
                    item.setToolTip(widget.DESCRIPTION)
                    if self.manager.config.is_placed(widget.NAME):
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    self.w_list.addItem(item)
                except:
                    print(traceback.format_exc())
            if not self.w_list.size().isEmpty():
                self.w_list.setCurrentRow(0)
        except:
            print(traceback.format_exc())

    def _list_click(self):
        try:
            item = self.w_list.currentItem()
            if not item:
                self.h_label.setText(self.lang['no_select'])
                return
            self.h_label.setText(self.manager.widgets[item.text()].DESCRIPTION)
        except:
            print(traceback.format_exc())

    def _list_double_click(self):
        try:
            item = self.w_list.currentItem()
            if not item:
                self.h_label.setText(self.lang['no_select'])
                return
            self.item_info = sys.modules['core.gui.gui'].ItemInfo(item.text())
        except:
            print(traceback.format_exc())

    def _delete(self):
        try:
            # check item
            item = self.w_list.currentItem()
            if not item:  # check selected
                self.h_label.setText(self.lang['no_select'])
                return
            # create message box
            mbox = QMessageBox(QMessageBox.Question,
                               self.lang['del_mbox_title'],
                               self.lang['del_mbox_text'].format(item.text()),
                               QMessageBox.Yes | QMessageBox.No, self)
            yes = mbox.button(QMessageBox.Yes)
            yes.setText(self.lang['del_mbox_yes_button'])
            yes.setToolTip(self.lang['del_mbox_yes_button_tt'])
            no = mbox.button(QMessageBox.No)
            no.setText(self.lang['del_mbox_no_button'])
            no.setToolTip(self.lang['del_mbox_no_button_tt'])
            # process
            if mbox.exec() == QMessageBox.Yes:
                self.manager.delete_widget(item.text())
                self._list_fill()
        except:
            print(traceback.format_exc())

    def _arch_delete(self):
        try:
            pass
        except:
            print(traceback.format_exc())


class ArchDelete(QWidget):
    def __init__(self, locale, manager):
        """

        :param locale: dict, current locale
        :param manager: WidgetManager class
        """
        # init
        QWidget.__init__(self)
        self.manager = manager
        self.lang = locale['ARCH_DELETE']
