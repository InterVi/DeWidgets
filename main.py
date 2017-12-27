#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import traceback
from PyQt5.QtWidgets import QApplication
import core.gui.gui as gui
from core.paths import STDERR_LOG, STDOUT_LOG

TIME_FORMAT = '%Y-%m-%d %X'

if __name__ == '__main__':
    # setup streams
    err = open(STDERR_LOG, 'a', encoding='utf-8')
    out = open(STDOUT_LOG, 'a', encoding='utf-8')
    sys.stderr = err
    sys.stdout = out
    try:
        # start
        print('[' + time.strftime(TIME_FORMAT) + '] start')
        app = QApplication(sys.argv)
        gui.__init__(app)
        # exit
        status = app.exec()  # waiting
        sys.exit(status)
    except SystemExit as se:
        print('exit code ' + str(se))
    except:
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
        try:
            print('[' + time.strftime(TIME_FORMAT) + '] stop')
            out.close()
            err.close()
        except:
            print(traceback.format_exc())
