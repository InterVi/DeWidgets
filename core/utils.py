"""All utils for using in widgets and core."""
import logging
import traceback
from enum import IntEnum


STDOUT = logging.getLogger('stdout')
"""stdout logger"""
STDERR = logging.getLogger('stderr')
"""stderr logger"""
CONS = logging.getLogger()
"""main logger (console output and writing to stdout)"""


class LogLevel(IntEnum):
    """logging levels"""
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @staticmethod
    def from_string(s) -> int:
        """Get int level from string key.

        :param s: str, key
        :return: int, level (not enum) (raise NameError if not found)
        """
        if s in LogLevel._member_names_:
            return int(LogLevel._member_map_[s])
        raise NameError(str(s) + ' not found')

    @staticmethod
    def from_int(num) -> str:
        """Get string key from int level.

        :param num: int, level
        :return: str, key (raise ValueError if not found)
        """
        if num == logging.NOTSET:
            return 'NOTSET'
        elif num == logging.DEBUG:
            return 'DEBUG'
        elif num == logging.INFO:
            return 'INFO'
        elif num == logging.WARNING:
            return 'WARNING'
        elif num == logging.ERROR:
            return 'ERROR'
        elif num == logging.CRITICAL:
            return 'CRITICAL'
        else:
            raise ValueError(str(num) + ' not found')

    @staticmethod
    def get_keys() -> tuple:
        """Get all string keys.

        :return: tuple, str keys
        """
        return tuple(LogLevel._member_names_)


def try_except(except_func=None, ex_args=(), ex_kwargs=(),
               level=LogLevel.ERROR):
    """Wrap try-except block. Stacktrace will printed to stdout (log file).
    Wrapped function or except_func will return original value.

    :param except_func: call if exception
    :param ex_args: arguments for except_func
    :param ex_kwargs: dict arguments for except_func
    :param level: LogLevel, logging level
    :return: wrapped function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                STDOUT.log(int(level), traceback.format_exc())
                if except_func:
                    try:
                        return except_func(*ex_args, **ex_kwargs)
                    except:
                        STDOUT.log(int(level), traceback.format_exc())
                        print('Except args: ' + str(ex_args))
                        print('Except kwargs: ' + str(ex_kwargs))
                print('Args: ' + str(args))
                print('Kwargs: ' + str(kwargs))

        return wrapper

    return decorator


def print_stack_trace(level=LogLevel.ERROR):
    """Print stacktrace to stdout logger. Example: print_stack_trace()()

    :param level: LogLevel, logging level
    :return: lambda function (for create correct trace)
    """
    return lambda: STDOUT.log(int(level), traceback.format_exc())
