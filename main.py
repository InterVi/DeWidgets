#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import traceback
from PyQt5.QtWidgets import QApplication
import core.gui.gui as gui
from core.paths import STDERR_LOG, STDOUT_LOG, LOCK_FILE

if __name__ == '__main__':
    # setup streams
    err = open(STDERR_LOG, 'a', encoding='utf-8')
    out = open(STDOUT_LOG, 'a', encoding='utf-8')
    sys.stderr = err
    sys.stdout = out
    try:
        # start
        app = QApplication(sys.argv)
        gui.__init__(app)
        # exit
        status = app.exec()  # waiting
        sys.exit(status)
    except SystemExit as se:
        status = 1
        print('exit code ' + str(se))
        # pass
    except:
        status = 1
        print(traceback.format_exc())
    finally:  # correct exit
        try:
            gui.manager.unload_all()
        except:
            print(traceback.format_exc())
        try:
            gui.manager.config.save()
        except:
            print(traceback.format_exc())
        if status != 2:
            if os.path.isfile(LOCK_FILE):  # remove lock file
                os.remove(LOCK_FILE)
