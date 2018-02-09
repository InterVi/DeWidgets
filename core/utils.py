"""All utils for using in widgets and core."""
import traceback


def try_except(func, except_func=None, ex_args=(), ex_kwargs={}):
    """Wrap try-except block. Stacktrace will printed to stdout (log file).

    :param func: function for try-except block
    :param except_func: call if exception
    :param ex_args: arguments for except_func
    :param ex_kwargs: dict arguments for except_func
    :return: wrapped function
    """
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            print(traceback.format_exc())
            if except_func:
                try:
                    except_func(*ex_args, **ex_kwargs)
                except:
                    print(traceback.format_exc())
                    print('Except args: ' + str(ex_args))
                    print('Except kwargs: ' + str(ex_kwargs))
            print('Args: ' + str(args))
            print('Kwargs: ' + str(kwargs))

    return wrapper
