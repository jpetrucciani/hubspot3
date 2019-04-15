"""
hubspot leads api
"""
import time
from hubspot3.base import BaseClient
from hubspot3 import logging_helper


LEADS_API_VERSION = "1"


def list_to_snake_dict(list_):
    dictionary = {}
    for item in list_:
        dictionary[item] = item
        if item.lower() != item:
            python_variant = item[0].lower() + "".join(
                [c if c.lower() == c else "_{}".format(c.lower()) for c in item[1:]]
            )
            dictionary[python_variant] = item
    return dictionary


SORT_OPTIONS = [
    "firstName",
    "lastName",
    "email",
    "address",
    "phone",
    "insertedAt",
    "fce.convertDate",
    "lce.convertDate",
    "lastModifiedAt",
    "closedAt",
]
SORT_OPTIONS_DICT = list_to_snake_dict(SORT_OPTIONS)
TIME_PIVOT_OPTIONS = [
    "insertedAt",
    "firstConvertedAt",
    "lastConvertedAt",
    "lastModifiedAt",
    "closedAt",
]
TIME_PIVOT_OPTIONS_DICT = list_to_snake_dict(TIME_PIVOT_OPTIONS)
SEARCH_OPTIONS = [
    "search",
    "sort",
    "dir",
    "max",
    "offset",
    "startTime",
    "stopTime",
    "timePivot",
    "excludeConversionEvents",
    "emailOptOut",
    "eligibleForEmail",
    "bounced",
    "isNotImported",
]
SEARCH_OPTIONS_DICT = list_to_snake_dict(SEARCH_OPTIONS)
BOOLEAN_SEARCH_OPTIONS = set(
    [
        "excludeConversionEvents",
        "emailOptOut",
        "eligibleForEmail",
        "bounced",
        "isNotImported",
    ]
)

MAX_BATCH = 100


class LeadsClient(BaseClient):
    """
    The hubspot3 Leads client uses the _make_request method to call the API for data.
    It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        super(LeadsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.leads")

    def camelcase_search_options(self, options):
        """change all underscored variants back to what the API is expecting"""
        new_options = {}
        for key in options:
            value = options[key]
            new_key = SEARCH_OPTIONS_DICT.get(key, key)
            if new_key == "sort":
                value = SORT_OPTIONS_DICT.get(value, value)
            elif new_key == "timePivot":
                value = TIME_PIVOT_OPTIONS_DICT.get(value, value)
            elif new_key in BOOLEAN_SEARCH_OPTIONS:
                value = str(value).lower()
            new_options[new_key] = value
        return new_options

    def _get_path(self, subpath):
        """get the full api url for the given subpath on this client"""
        return "leads/v{}/{}".format(
            self.options.get("version") or LEADS_API_VERSION, subpath
        )

    def get_lead(self, guid, **options):
        return self.get_leads(guid, **options)[0]

    def get_leads(self, *guids, **options):
        """Supports all the search parameters in the API as well as python underscored variants"""
        original_options = options
        options = self.camelcase_search_options(options.copy())
        params = {}
        for i, guid in enumerate(guids):
            params["guids[{}]".format(i)] = guid
        for k in list(options.keys()):
            if k in SEARCH_OPTIONS:
                params[k] = options[k]
                del options[k]
        leads = self._call("list/", params, **options)
        self.log.info(
            "retrieved {} leads through API ( {}options={} )".format(
                len(leads), guids and "guids={}, ".format(guids or ""), original_options
            )
        )
        return leads

    def retrieve_lead(self, *guid, **options):
        cur_guid = guid or ""
        params = {}
        for key in options:
            params[key] = options[key]
        # Set guid to -1 as default for not finding a user
        lead = {"guid": "-1"}
        # wrap lead call so that it doesn't error out when not finding a lead
        try:
            lead = self._call("lead/{}".format(cur_guid), params, **options)
        except Exception:
            # no lead here
            pass
        return lead

    def update_lead(self, guid, update_data=None, **options):
        update_data = update_data or {}
        update_data["guid"] = guid
        return self._call(
            "lead/{}/".format(guid), data=update_data, method="PUT", **options
        )

    def get_webhook(self, **options):  # WTF are these 2 methods for?
        return self._call("callback-url", **options)

    def register_webhook(self, url, **options):
        return self._call(
            "callback-url",
            params={"url": url},
            data={"url": url},
            method="POST",
            **options
        )

    def close_lead(self, guid, close_time=None, **options):
        return self.update_lead(
            guid, {"closedAt": close_time or int(time.time() * 1000)}, **options
        )

    def open_lead(self, guid, **options):
        self.update_lead(guid, {"closedAt": ""}, **options)
