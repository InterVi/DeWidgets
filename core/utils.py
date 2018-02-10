"""All utils for using in widgets and core."""
import traceback


def try_except(except_func=None, ex_args=(), ex_kwargs=()):
    """Wrap try-except block. Stacktrace will printed to stdout (log file).
    Wrapped function or except_func will return original value.

    :param except_func: call if exception
    :param ex_args: arguments for except_func
    :param ex_kwargs: dict arguments for except_func
    :return: wrapped function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                print(traceback.format_exc())
                if except_func:
                    try:
                        return except_func(*ex_args, **ex_kwargs)
                    except:
                        print(traceback.format_exc())
                        print('Except args: ' + str(ex_args))
                        print('Except kwargs: ' + str(ex_kwargs))
                print('Args: ' + str(args))
                print('Kwargs: ' + str(kwargs))

        return wrapper

    return decorator
