"""
base utils for the hubspot3 library
"""
import logging
import sys
from collections import OrderedDict
from typing import Dict, Union, List, Optional, Set


PY_VERSION = sys.version_info
MAXIMUM_REQUEST_LENGTH = 15500


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


def ordered_dict(dictionary: Dict) -> Union[Dict, OrderedDict]:
    """
    shim to fix some param ordering issues with python 3.5
    in python 3.6+, dictionaries are ordered by default
    """
    if PY_VERSION[0] == 3 and PY_VERSION[1] == 5:
        return OrderedDict(sorted(dictionary.items(), key=lambda x: x[0]))
    return dictionary


def split_properties(properties: Set[str],
                     max_properties_request_length: Optional[int] = None,
                     property_name: str = "properties") -> List[Set[str]]:
    """
    Split a set of properties in a list of sets of properties where the total length of
    "properties=..." for each property is smaller than the max
    """
    if max_properties_request_length is None:
        max_properties_request_length = MAXIMUM_REQUEST_LENGTH

    # property_name_len is its length plus the '=' at the end
    property_name_len = len(property_name) + 1

    current_length = 0
    properties_groups = []
    current_properties_group = []
    for single_property in properties:
        current_length += len(single_property) + property_name_len

        if current_length > max_properties_request_length:
            properties_groups.append(current_properties_group)
            current_length = 0
            current_properties_group = []

        current_properties_group.append(single_property)

    if len(current_properties_group) > 0:
        properties_groups.append(current_properties_group)

    return properties_groups


def clean_result(source_name, source_list, start_d, end_d):
    source_in_interval = []

    def date_format(source_name, item):
        if source_name == "deals":
            update_date = int(item["properties"]["hs_lastmodifieddate"]["value"])
        elif source_name == "engagements":
            update_date = item["engagement"]["lastUpdated"]
        elif source_name == "contacts":
            update_date = item["addedAt"]
        return update_date

    for item in source_list:
        update_date = date_format(source_name, item)
        if update_date >= start_d and update_date <= end_d:
            source_in_interval.append(item)
    return source_in_interval
