import os
import sys

PATH = os.path.join(sys.path[0], 'widgets')
sys.path.append(PATH)


def get_widgets() -> list:
    result = []
    for name in os.listdir(PATH):
        file = os.path.join(PATH, name)
        if not os.path.isfile(file) or name[-2:] != 'py'\
                or name[:-3] == '__init__':
            continue
        result.append(name[:-3])
    return result


__all__ = get_widgets()
