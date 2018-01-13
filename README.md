# DeWidgets

Qt5 widgets for desktop. Easy API for writing you custom widgets. Automatic save data in config file. Support multi language. Support install widgets from *ZIP* archive.

Require Python >= **3.5** version.

## Available widgets

* **Simple Notes** - colored sticky sheets
* **Timer** - multiple timers, popup alert and sound alarm
* **Minecraft Server Monitoring** - show online MC servers statistics with query
* **Digital Time** - show digital time and date
* **Crypto Note** - low secure note as passowrd (AES-256)
* **CPU Info** - show SPU information (load and freq)
* **RAM Info** - show RAM and swap information

## Commandline arguments

* **-h, --help** - show this help message and exit
* **-p** *PATH*, **--paths** *PATH* - Load config for use custom components paths.
* **-c** *PATH*, **--create** *PATH* - Create folders and files into the given path.

**Example for user separation**

```shell
DeWidgets -c /home/user/.dw
```

**-c** - creating folders and files, and/or using this path

## Install and startup

```shell
pip3 install PyQt5  # or pacman -S python-pyqt5
pip3 install mcstatus  # or yaourt -S mcstatus
pip3 install pycrypto  # or pacman -S python-crypto
pip3 insrall psutil  # or pacman -S python-psutil
git clone https://github.com/InterVi/DeWidgets.git
cd DeWidgets
python3 main.py
```

## Depends

* [PyQt5](https://github.com/baoboa/pyqt5)
* [mcstatus](https://github.com/Dinnerbone/mcstatus) (for *MC monitoring*)
* [pycrypto](https://github.com/dlitz/pycrypto) (for *Crypto Note*)
* [psutil](https://github.com/giampaolo/psutil) (for hardware monitors)

## How to create ZIP widget

**Archive structure**:

```
-DeWidgets.txt
-widget.py
-more_widgets.py
-res
--you_folder
---icon.png
-langs
--ru.conf
--more.conf
```

Please, using unique module (*.py files) names.
