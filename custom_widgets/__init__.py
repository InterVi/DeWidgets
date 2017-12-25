import os


def get_widgets() -> list:
    """Get names widgets.

    :return: list, names
    """
    path = os.path.abspath(os.path.dirname(__file__))
    result = []
    for name in os.listdir(path):
        file = os.path.join(path, name)
        if not os.path.isfile(file) or name[-2:] != 'py'\
                or name[:-3] == '__init__':
            continue
        result.append(name[:-3])
    return result
