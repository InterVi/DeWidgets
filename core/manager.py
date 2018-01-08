"""Manage widgets."""
import os
import sys
import inspect
import traceback
from distutils.util import strtobool
from configparser import ConfigParser
from importlib.machinery import SourceFileLoader
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import widgets as w
from core.paths import CONF_WIDGETS, WIDGET, C_WIDGETS

sys.path.append(C_WIDGETS)
CUSTOM_WIDGETS = SourceFileLoader('__init__',
                                  os.path.join(C_WIDGETS, '__init__.py')
                                  ).load_module()
"""Custom widgets module for *use get_widgets(path)* function."""


class Widget:
    """the class is inherited by widgets"""
    def __init__(self, widget_manager):
        self.widget_manager = widget_manager
        self.NAME = 'none'
        self.DESCRIPTION = 'none'
        self.HELP = 'none'
        self.AUTHOR = 'none'
        self.EMAIL = 'none'
        self.URL = 'none'
        self.ICON = QIcon(WIDGET)

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
        """remove widget from desktop (before call destroy)."""
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
        """Widgets dict, key - name, value - widget object (Main class)."""
        self.custom_widgets = []
        """Custom widgets names list."""
        self.paths = {}
        """Paths to widget files. Keys - names, values - paths to files."""
        self.config = ConfigManager(self)
        """ConfigManager class"""
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
        for name in self.config.config:
            if name == 'DEFAULT' or name in self.widgets:
                continue
            if placed and self.config.is_placed(name):
                self.load(self.config.config[name]['file'])
            elif not placed and not self.config.is_placed(name):
                self.load(self.config.config[name]['file'])

    def load_new(self):
        """Loading only new widgets (not loaded before)."""
        for name in w.get_widgets():
            if name not in sys.modules:
                self.load(name)
        for name in CUSTOM_WIDGETS.get_widgets():
            if name not in sys.modules:
                self.load(name)

    def load(self, name):
        """Load widget from module.

        :param name: str, module name
        """
        try:
            mod = __import__(name)
            if 'Main' not in mod.__dict__ or not callable(mod.Main):
                del sys.modules[name]
                return
            if 'not_loading' in mod.__dict__ and mod.__dict__['not_loading']:
                del sys.modules[name]
                return
            widget = mod.Main(self)
            widget.load()
            widget.setWindowFlags(Qt.CustomizeWindowHint |
                                  Qt.WindowStaysOnBottomHint | Qt.Tool)
            widget.setWindowTitle(widget.NAME)
            widget.setWindowIcon(widget.ICON)
            self.widgets[widget.NAME] = widget
            self.config.load(widget.NAME)
            self.paths[widget.NAME] = mod.__file__
            if os.path.dirname(mod.__file__) == C_WIDGETS:
                self.custom_widgets.append(widget.NAME)
        except:
            print(traceback.format_exc())

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
            self.config.set_placed(name, False)
            if reminconf:
                self.config.remove(name)
            self.config.save()
        except:
            print(traceback.format_exc())

    def delete_widget(self, name):
        """Remove widget file (after remove widget data from config
        and unload.

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
            os.remove(path)
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

    def unload_all(self):
        """Unload all loaded widgets."""
        for name in list(self.widgets.keys()):
            self.unload(name)

    def unload_hidden(self):
        """Unload only hidden (not placed) widgets."""
        for name in list(self.widgets.keys()):
            if self.widgets[name].isHidden():
                self.unload(name)

    def edit_mode(self, mode, name=None) -> bool:
        """Call widget event and save config.
        
        :param mode: True - edit on
        :param name: widget name (no call other widgets)
        :return: bool, True - success call and save config
        """
        def save(widget):
            try:
                if widget.isHidden():
                    return
                widget.edit_mode(mode)
                if not mode:
                    self.config.add(widget.NAME)
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
