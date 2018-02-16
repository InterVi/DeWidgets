#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import inspect
import logging
from configparser import RawConfigParser
from PyQt5.QtWidgets import QApplication
import core.gui.gui as gui
from core.paths import STDERR_LOG, STDOUT_LOG, CONF_SETTINGS
from core.utils import try_except, print_stack_trace
import core.lock as lock


class StreamProxy:
    """for replace stdout and stderr streams"""
    def __init__(self, logger):
        self.logger = logger

    def write(self, buf):
        (file, number, func, lines, index) =\
            inspect.getframeinfo(inspect.currentframe().f_back)
        for line in buf.rstrip().splitlines():
            self.logger.info(os.path.basename(file) + ':' + str(number) +
                             ' -> ' + line.rstrip())

    def flush(self):
        pass

    def close(self):
        pass


def get_file_handler(path, log_format):
    handler = logging.FileHandler(path, encoding='utf-8')
    handler.setLevel(logging.NOTSET)
    handler.setFormatter(logging.Formatter(log_format))
    return handler


@try_except()
def __setup_loggers(prop):
    level = int(prop['LOGS']['log_level'])
    out_format = prop['LOGS']['stdout']
    err_format = prop['LOGS']['stderr']
    logging.basicConfig(format=prop['LOGS']['CONS'], level=level)

    stdout = logging.getLogger('stdout')
    stdout.setLevel(level)
    stdout.addHandler(get_file_handler(STDOUT_LOG, out_format))

    stderr = logging.getLogger('stderr')
    stderr.setLevel(level)
    stderr.addHandler(get_file_handler(STDERR_LOG, err_format))

    sys.stdout = StreamProxy(stdout)
    sys.stderr = StreamProxy(stderr)


@try_except()
def __start():
    prop = RawConfigParser()
    prop.read(CONF_SETTINGS, 'utf-8')
    __setup_loggers(prop)
    try:
        # start
        logging.getLogger('stdout').info('start')
        app = QApplication(sys.argv)
        gui.__init__(app, prop)
        # exit
        status = app.exec()  # waiting
        sys.exit(status)
    except SystemExit as se:
        logging.getLogger('stdout').info('exit code: ' + str(se))
    except:
        print_stack_trace()()
    finally:  # correct exit
        try:  # unload widgets
            gui.manager.unload_all()
        except:
            print_stack_trace()()
        try:  # save widgets config
            gui.manager.config.save()
        except:
            print_stack_trace()()
        try:  # remove lock file
            lock.remove_lock()
        except:
            print_stack_trace()()


if __name__ == '__main__':
    __start()
