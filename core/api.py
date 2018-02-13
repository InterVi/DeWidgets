"""API for widgets (classes for inherit)."""
from PyQt5.QtGui import QIcon
from core.paths import WIDGET


class WidgetInfo:
    """widget information"""

    def __init__(self, lang):
        """

        :param lang: ConfigParser locale dict
        """
        self.lang = lang
        self.NAME = 'none'
        self.VERSION = '1.0'
        self.DESCRIPTION = 'none'
        self.HELP = 'none'
        self.AUTHOR = 'none'
        self.EMAIL = 'none'
        self.URL = 'none'
        self.ICON = QIcon(WIDGET)


class Widget:
    """the class is inherited by widgets"""

    def __init__(self, widget_manager, info):
        """

        :param widget_manager: WidgetManager object
        :param info: WidgetInfo object
        """
        self.widget_manager = widget_manager
        self.info = info

    def load(self):
        """load widget event (before setup window flags and other)"""
        pass

    def end_loading(self):
        """call when all the widgets are loaded (when you start the app)."""
        pass

    def load_other(self, name):
        """load other widget event (after loading).

        :param name: str, widget name
        """
        pass

    def unload_other(self, name):
        """unload other widget event (before unloading).

        :param name: str, widget name
        """
        pass

    def unload(self):
        """unload widget event (before call destroy)."""
        pass

    def place(self):
        """place widget for desktop event (before call show)."""
        pass

    def boot(self):
        """auto-place widget for desktop event (before call show)"""
        pass

    def hide_event(self, state):
        """hide from tray context menu event (before call setHidden)

        :param state: bool, True - hide, False - unhide
        """
        pass

    def edit_mode(self, mode):
        """edit mode checkbox event

        :param mode: True or False
        """
        pass

    def show_settings(self):
        """show widget settings window"""
        pass

    def remove(self):
        """remove widget from desktop (before call destroy and unload)."""
        pass

    def purge(self):
        """purge widget and all data (before call unload)."""
        pass

    def purge_other(self, name, reminconf):
        """purge other widget event (before purging).

        :param name: str, widget name
        :param reminconf: bool, True - remove widget all data from config
        """
        pass

    def delete_widget(self):
        """Remove widget files (before call purge and unload or only unload).
        If widget not placed, load will not calling - only this before unload.
        """
        pass

    def delete_other_widget(self, name):
        """delete other widget event (see delete_widget) (before deleting).

        :param name: str, widget name
        """
        pass