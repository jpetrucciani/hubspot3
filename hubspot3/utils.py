"""
base utils for the hubspot3 library
"""
import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def get_log(name):
    logger = logging.getLogger(name)
    logger.addHandler(NullHandler())
    return logger


def force_utf8(raw):
    """Will force the string to convert to valid utf8"""
    string = raw
    try:
        string = string.decode("utf-8", "ignore")
    except Exception:
        pass
    return string


def prettify(obj_with_props, id_key):
    prettified = {
        prop: obj_with_props["properties"][prop]["value"]
        for prop in obj_with_props["properties"]
    }
    prettified["id"] = obj_with_props[id_key]
    try:
        prettified.update(
            {
                assoc: obj_with_props["associations"][assoc]
                for assoc in obj_with_props["associations"]
            }
        )
    except KeyError:
        pass

    return prettified
