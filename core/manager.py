"""Manage widgets."""
import os
import sys
import inspect
import traceback
from distutils.util import strtobool
from configparser import ConfigParser
from importlib.machinery import SourceFileLoader
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import widgets as w
from core.paths import CONF_WIDGETS, WIDGET, C_WIDGETS

sys.path.append(C_WIDGETS)
CUSTOM_WIDGETS = SourceFileLoader('__init__',
                                  os.path.join(C_WIDGETS, '__init__.py')
                                  ).load_module()
"""Custom widgets module for *use get_widgets(path)* function."""


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

    def delete_widget(self):
        """remove widget files (before call purge and unload)"""
        pass


class WidgetManager:
    """manage widgets"""
    def __init__(self, lang, c_lang, main):
        """

        :param lang: ConfigParser locale dict
        :param c_lang: ConfigParser locale dict for custom widgets
        :param main: gui module
        """
        self.lang = lang
        """ConfigParser dict, current locale."""
        self.c_lang = c_lang
        """ConfigParser dict, current locale for custom widgets"""
        self.widgets = {}
        """Widgets dict, key - name, value - widget object (Main object)."""
        self.info = {}
        """WidgetInfo dict, key - name, value - WidgetInfo object"""
        self.custom_widgets = []
        """Custom widgets names list."""
        self.paths = {}
        """Paths to widget files. Keys - names, values - paths to files."""
        self.config = ConfigManager(self)
        """ConfigManager object"""
        self.main_gui = main
        """core.gui.gui module"""

    def load_all(self):
        """Loading all widgets."""
        for name in w.get_widgets():
            self.load(name)
        for name in CUSTOM_WIDGETS.get_widgets():
            self.load(name)

    def load_placed(self, placed=True):
        """Loading placed widgets.

        :param placed: bool, True - only placed, False - only hidden
        """
        if not placed:
            for name in w.get_widgets():
                if name not in self.paths:
                    self.load(name)
            for name in CUSTOM_WIDGETS.get_widgets():
                if name not in self.paths:
                    self.load(name)
            return
        for name in self.config.config:
            if name == 'DEFAULT' or name in self.widgets:
                continue
            if self.config.is_placed(name):
                self.load(self.config.config[name]['file'])

    def load_new(self):
        """Loading only new widgets (not loaded before)."""
        for name in w.get_widgets():
            if name not in sys.modules:
                self.load(name)
        for name in CUSTOM_WIDGETS.get_widgets():
            if name not in sys.modules:
                self.load(name)

    def load(self, name, only_info=True) -> bool:
        """Load widget from module.

        :param name: str, module name
        :param only_info: bool, if True - load only WidgetInfo classes
        :return: True if load correctly
        """
        try:
            if name in sys.modules:  # get module
                mod = sys.modules[name]
            else:  # import module
                mod = __import__(name)
            # validate
            if 'not_loading' in mod.__dict__ and mod.__dict__['not_loading']:
                del sys.modules[name]
                return False
            if 'Main' not in mod.__dict__ or not callable(mod.Main):
                del sys.modules[name]
                return False
            if 'Info' not in mod.__dict__ or not callable(mod.WidgetInfo):
                del sys.modules[name]
                return False
            # get and validate WidgetInfo
            info = mod.Info(self.lang)
            if not isinstance(info, WidgetInfo):
                del sys.modules[name]
                return False
            # fill data
            if os.path.dirname(mod.__file__) == C_WIDGETS and\
                    info.NAME not in self.custom_widgets:
                self.custom_widgets.append(info.NAME)
            self.info[info.NAME] = info
            self.paths[info.NAME] = mod.__file__
            if only_info and not self.config.is_placed(info.NAME):
                return True
            # validate Widget
            widget = mod.Main(self, info)
            if not isinstance(widget, Widget) or\
                    not isinstance(widget, QWidget):
                del sys.modules[name]
                return False
            # load Main class
            widget.load()
            widget.setWindowFlags(Qt.CustomizeWindowHint |
                                  Qt.WindowStaysOnBottomHint | Qt.Tool)
            widget.setWindowTitle(info.NAME)
            widget.setWindowIcon(info.ICON)
            self.widgets[info.NAME] = widget
            self.config.load(info.NAME)
            return True
        except:
            print(traceback.format_exc())
            if name in sys.modules:
                del sys.modules[name]
            return False

    def remove(self, name, reminconf=False):
        """Remove widget from desktop.

        :param name: str, module name
        :param reminconf: bool, True - remove widget all data from config
        """
        try:
            if reminconf:
                try:
                    self.widgets[name].purge()
                except:
                    print(traceback.format_exc())
            else:
                try:
                    self.widgets[name].remove()
                except:
                    print(traceback.format_exc())
                self.config.add(name)
            self.widgets[name].hide()
            self.widgets[name].destroy()
            self.unload(name)
            self.config.set_placed(name, False)
            if reminconf:
                self.config.remove(name)
            self.config.save()
        except:
            print(traceback.format_exc())

    def delete_widget(self, name):
        """Remove widget file (after remove widget data from config
        and unload). For only placed widgets.

        :param name: str, widget name
        """
        try:
            path = self.paths[name]
            try:
                self.widgets[name].delete_widget()
            except:
                print(traceback.format_exc())
            self.remove(name, True)
            try:
                self.widgets[name].unload()
            except:
                print(traceback.format_exc())
            self.unload(name)
            self.config.remove(name)  # warranty
            self.del_from_dicts(name)
            os.remove(path)
        except:
            print(traceback.format_exc())

    def del_from_dicts(self, name):
        """Remove data from info, paths dict and custom_widgets.

        :param name: str, widget name
        """
        try:
            del self.info[name]
            del self.paths[name]
            if name in self.custom_widgets:
                self.custom_widgets.remove(name)
        except:
            print(traceback.format_exc())

    def unload(self, name):
        """Unload widget in memory. Destroy.

        :param name: str, widget name
        """
        try:
            try:
                self.widgets[name].unload()
                self.widgets[name].destroy()
            except:
                print(traceback.format_exc())
            del self.widgets[name]
            del sys.modules[os.path.basename(self.paths[name])[:-3]]
            if name in self.custom_widgets:
                self.custom_widgets.remove(name)
        except:
            print(traceback.format_exc())

    def unload_all(self, del_from_dicts=True):
        """Unload all loaded widgets.

        :param del_from_dicts: bool, if True - like del_from_dicts"""
        for name in list(self.widgets.keys()):
            self.unload(name)
        if del_from_dicts:
            self.info.clear()
            self.paths.clear()
            self.custom_widgets.clear()

    def del_data_no_placed(self):
        """Remove data (from info and paths) only not placed widgets."""
        for name in list(self.info.keys()):
            if name not in self.widgets:
                self.del_from_dicts(name)

    def is_placed(self) -> bool:
        """Check the presence of widgets on the desktop.

        :return: True if at least one placed
        """
        for widget in self.widgets.values():
            if widget.isVisible():
                return True
        return False

    def get_config(self, name) -> dict:
        """Get config section for widget.

        :param name: str, widget name
        :return: dict, config section for widget in ConfigParser
        """
        return self.config.config[name]

    def edit_mode(self, mode, name=None) -> bool:
        """Call widget event and save config.
        
        :param mode: True - edit on
        :param name: widget name (no call other widgets)
        :return: bool, True - success call and save config
        """
        def save(widget):
            try:
                widget.edit_mode(mode)
                if not mode:
                    self.config.add(widget.info.NAME)
            except:
                print(traceback.format_exc())

        if name and name in self.widgets:
            save(self.widgets[name])
            self.config.save()
            return True
        elif not name:
            for w_object in self.widgets.values():
                save(w_object)
            self.config.save()
            return True
        else:
            return False


class ConfigManager:
    """manage config"""
    def __init__(self, widget_manager):
        self.wm = widget_manager
        self.config = ConfigParser()
        try:
            if os.path.isfile(CONF_WIDGETS):
                self.config.read(CONF_WIDGETS, 'UTF-8')
        except:
            print(traceback.format_exc())

    def load_all(self):
        """Load (setup) only configured widgets."""
        for name in self.config:
            if name not in self.wm.widgets:
                continue
            self.load(name)

    def load(self, name):
        """Setup widget (set size, position, opacity, call boot and show.

        :param name: str, widget name
        """
        try:
            if name not in self.config or name not in self.wm.widgets:
                return
            prop = self.config[name]
            if not prop:
                return
            widget = self.wm.widgets[name]
            widget.resize(int(prop['width']), int(prop['height']))
            widget.move(int(prop['x']), int(prop['y']))
            widget.setWindowOpacity(float(prop['opacity']))
            if self.is_placed(name):
                # if placed, show window
                widget.boot()
                widget.show()
        except:
            print(traceback.format_exc())

    def save(self):
        """Save config to file."""
        try:
            with open(CONF_WIDGETS, 'w', encoding='UTF-8') as config:
                self.config.write(config)
        except:
            print(traceback.format_exc())

    def add(self, name):
        """Add or update widget data in config (not call save).
        Size, position, opacity, placed, file (module name).

        :param name: str, widget name
        """
        try:
            widget = self.wm.widgets[name]
            if name in self.config:
                sec = self.config[name]
                sec['width'] = str(widget.width())
                sec['height'] = str(widget.height())
                sec['x'] = str(widget.x())
                sec['y'] = str(widget.y())
                sec['opacity'] = str(widget.windowOpacity())
                sec['placed'] = str(not widget.isHidden())
                sec['file'] = os.path.basename(inspect.getfile(widget.__class__
                                                               ))[:-3]
            else:
                self.config[name] = {
                    'width': str(widget.width()),
                    'height': str(widget.height()),
                    'x': str(widget.x()),
                    'y': str(widget.y()),
                    'opacity': str(widget.windowOpacity()),
                    'placed': str(not widget.isHidden()),
                    'file': os.path.basename(inspect.getfile(widget.__class__)
                                             )[:-3]
                }
        except:
            print(traceback.format_exc())

    def remove(self, name):
        """Remove widget data from config (not call save).

        :param name: str, widget name
        """
        try:
            if name in self.config:
                del self.config[name]
        except:
            print(traceback.format_exc())

    def set_placed(self, name, value):
        """Set placed status.

        :param name: str, widget name
        :param value: bool, True - if placed to desktop
        """
        try:
            self.config[name]['placed'] = str(value)
        except:
            print(traceback.format_exc())

    def is_placed(self, name) -> bool:
        """Check widget placed.

        :param name: str, widget name
        :return: bool, True - if widget placed to desktop
        """
        if name in self.config:
            return bool(strtobool(self.config[name]['placed']))
        else:
            return False

    def create(self, name):
        """Create section (empty dict) in config for widget.

        :param name: str, widget name
        """
        try:
            if name not in self.config:
                self.config[name] = {}
        except:
            print(traceback.format_exc())

    def save_positions(self):
        """Save widget positions to config file."""
        try:
            for name in self.wm.widgets:
                self.add(name)
            self.save()
        except:
            print(traceback.format_exc())
