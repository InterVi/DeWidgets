"""Manage widgets."""
import os
import inspect
import traceback
from configparser import ConfigParser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import widgets as w
from core.paths import CONF_WIDGETS, WIDGET


class Widget:
    """the class is inherited by widgets"""
    def __init__(self, widget_manager):
        self.widget_manager = widget_manager
        self.NAME = 'none'
        self.DESCRIPTION = 'none'
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
        """remove widget in desktop (before call close)."""
        pass

    def purge(self):
        """purge widget and all data (before call close)."""
        pass


class WidgetManager:
    """manage widgets"""
    def __init__(self, lang, main):
        self.lang = lang
        """ConfigParser dict, current locale."""
        self.widgets = {}
        """Widgets dict, key - name, value - widget object (Main class)."""
        self.config = ConfigManager(self)
        """ConfigManager class"""
        self.main_gui = main
        """core.gui.gui module"""

    def load_all(self):
        for name in w.get_widgets():
            self.load(name)

    def load_placed(self, placed=True):
        for name in self.config.config:
            if name == 'DEFAULT' or name in self.widgets:
                continue
            if placed and self.config.config[name]['placed'] == 'True':
                self.load(self.config.config[name]['file'])
            elif not placed and self.config.config[name]['placed'] != 'True':
                self.load(self.config.config[name]['file'])
        for name in w.get_widgets():
            if name not in self.widgets and name not in self.config.config:
                self.load(name)

    def load_new(self):
        for name in w.get_widgets():
            if name not in self.widgets:
                self.load(name)

    def load(self, name):
        try:
            mod = __import__(name)
            if 'Main' not in mod.__dict__ or not callable(mod.Main):
                return
            if 'not_loading' in mod.__dict__:
                return
            widget = mod.Main(self)
            widget.load()
            widget.setWindowFlags(Qt.CustomizeWindowHint |
                                  Qt.WindowStaysOnBottomHint | Qt.Tool)
            widget.setWindowTitle(widget.NAME)
            widget.setWindowIcon(widget.ICON)
            self.widgets[widget.NAME] = widget
            self.config.load(widget.NAME)
        except:
            print(traceback.format_exc())

    def remove(self, name, reminconf=False):
        try:
            if reminconf:
                self.widgets[name].purge()
                self.widgets[name].setHidden(True)
                self.widgets[name].destroy()
                self.config.remove(name)
            else:
                self.widgets[name].remove()
                self.widgets[name].setHidden(True)
                self.widgets[name].destroy()
                self.config.add(name)
            self.config.save()
        except:
            print(traceback.format_exc())

    def unload(self, name):
        try:
            self.widgets[name].unload()
            self.widgets[name].destroy()
            del self.widgets[name]
        except:
            print(traceback.format_exc())

    def unload_all(self):
        for name in list(self.widgets.keys()):
            self.unload(name)

    def unload_hidden(self):
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
        for name in self.config:
            if name not in self.wm.widgets:
                continue
            self.load(name)

    def load(self, name):
        try:
            if name not in self.config or name not in self.wm.widgets:
                return
            prop = self.config[name]
            widget = self.wm.widgets[name]
            widget.resize(int(prop['width']), int(prop['height']))
            widget.move(int(prop['x']), int(prop['y']))
            widget.setWindowOpacity(float(prop['opacity']))
            if prop['placed'].lower() in ('true', 'yes', 'on'):
                # if placed, show window
                widget.boot()
                widget.show()
        except:
            print(traceback.format_exc())

    def save(self):
        try:
            with open(CONF_WIDGETS, 'w', encoding='UTF-8') as config:
                self.config.write(config)
        except:
            print(traceback.format_exc())

    def add(self, name):
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
        try:
            if name in self.config:
                del self.config[name]
        except:
            print(traceback.format_exc())

    def set_placed(self, name, value):
        try:
            self.config[name]['placed'] = value
        except:
            print(traceback.format_exc())

    def is_placed(self, name) -> bool:
        if name in self.config\
                and self.config[name]['placed'].lower() in ('true', 'yes'):
            return True
        else:
            return False
