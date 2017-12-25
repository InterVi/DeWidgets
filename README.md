# DeWidgets

Qt5 widgets for desktop. Easy API for writing you custom widgets. Automatic save data in config file. Support multi language. Support install widgets from *ZIP* archive.

## Install and startup

```shell
pip3 install PyQt5
pip3 install mcstatus
git clone https://github.com/InterVi/DeWidgets.git
cd DeWidgets
python3 main.py
```

## Available widgets

* **Simple Notes** - colored sticky sheets
* **Timer** - multiple timers, popup alert and sound alarm
* **Minecraft Server Monitoring** - show online MC servers statistics with query

## Depends

* PyQt5
* [mcstatus](https://github.com/Dinnerbone/mcstatus) (for *MC monitoring*)

## How to create ZIP widget

**Archive structure**:

```
-DeWidgets
-widget.py
-more_widgets.py
-res
--you_folder
---icon.png
-langs
--ru.conf
--more.conf
```

**Code example**

```python
import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon
from core.manager import Widget
from core.paths import C_RES

not_loading = True


class Main(Widget, QWidget):
    def __init__(self, widget_manager):
        # init
        Widget.__init__(self, widget_manager)
        QWidget.__init__(self)
        self.lang = widget_manager.c_lang['C_EXAMPLE']
        # setup widget
        self.NAME = 'Example Custom Widget'
        self.DESCRIPTION = self.lang['description']
        self.HELP = self.lang['help']
        self.AUTHOR = 'InterVi'
        self.EMAIL = 'intervionly@gmail.com'
        self.URL = 'https://github.com/InterVi/DeWidgets'
        self.ICON = QIcon(os.path.join(RES, 'example', 'icon.png'))
```
