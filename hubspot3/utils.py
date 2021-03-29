"""
base utils for the hubspot3 library
"""
import logging
import sys
from collections import OrderedDict
from urllib import parse
from typing import Dict, Union


PY_VERSION = sys.version_info


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def get_log(name: str):
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


def uglify_hapikey(url: str) -> str:
    """
    Uglifies the API key on a HubSpot URL
    """
    url_parse = parse.urlparse(url)
    parse_query = parse.parse_qs(url_parse.query)
    if "hapikey" not in parse_query:
        return url
    parse_query["hapikey"][0] = "{}****".format(parse_query["hapikey"][0][0:4])
    parse_result = parse.ParseResult(
        scheme=url_parse.scheme,
        netloc=url_parse.netloc,
        path=url_parse.path,
        params=url_parse.params,
        query=parse.urlencode(parse_query, doseq=True, safe="*"),
        fragment=url_parse.fragment,
    )
    return parse.urlunparse(parse_result)


def ordered_dict(dictionary: Dict) -> Union[Dict, OrderedDict]:
    """
    shim to fix some param ordering issues with python 3.5
    in python 3.6+, dictionaries are ordered by default
    """
    if PY_VERSION[0] == 3 and PY_VERSION[1] == 5:
        return OrderedDict(sorted(dictionary.items(), key=lambda x: x[0]))
    return dictionary
