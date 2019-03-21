"""
hubspot deals api
"""
from hubspot3 import logging_helper
from hubspot3.base import BaseClient
from hubspot3.utils import prettify

import urllib.parse

DEALS_API_VERSION = "1"


class DealsClient(BaseClient):
    """
    The hubspot3 Deals client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json return
    """

    def __init__(self, *args, **kwargs):
        super(DealsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.deals")

    def _get_path(self, subpath):
        return "deals/v{}/{}".format(
            self.options.get("version") or DEALS_API_VERSION, subpath
        )

    def get(self, deal_id, **options):
        return self._call("deal/{}".format(deal_id), method="GET", **options)

    def create(self, data=None, **options):
        data = data or {}
        return self._call("deal/", data=data, method="POST", **options)

    def update(self, key, data=None, **options):
        data = data or {}
        return self._call("deal/{}".format(key), data=data, method="PUT", **options)

    def associate(self, deal_id, object_type, object_ids, **options):
        # Encoding the query string here since HubSpot is expecting the "id" parameter to be
        # repeated for each object ID, which is not a standard practice and won't work otherwise.
        object_ids = [("id", object_id) for object_id in object_ids]
        query = urllib.parse.urlencode(object_ids)

        return self._call(
            "deal/{}/associations/{}".format(deal_id, object_type),
            method="PUT",
            query=query,
            **options
        )

    def get_all(self, offset=0, extra_properties=None, **options):
        """
        get all deals in the hubspot account.
        extra_properties: a list used to extend the properties fetched
        """
        finished = False
        output = []
        querylimit = 250  # Max value according to docs

        # default properties to fetch
        properties = [
            "associations",
            "dealname",
            "dealstage",
            "pipeline",
            "hubspot_owner_id",
            "description",
            "closedate",
            "amount",
            "dealtype",
            "createdate",
        ]

        # append extras if they exist
        if extra_properties:
            if isinstance(extra_properties, list):
                properties += extra_properties
            if isinstance(extra_properties, str):
                properties.append(extra_properties)

        while not finished:
            batch = self._call(
                "deal/paged",
                method="GET",
                params={
                    "limit": querylimit,
                    "offset": offset,
                    "properties": properties,
                    "includeAssociations": True,
                },
                doseq=True,
                **options
            )
            output.extend(
                [
                    prettify(deal, id_key="dealId")
                    for deal in batch["deals"]
                    if not deal["isDeleted"]
                ]
            )
            finished = not batch["hasMore"]
            offset = batch["offset"]

        return output

    def get_recently_created(
        self, limit=100, offset=0, since=None, include_versions=False, **options
    ):
        """
        get recently created deals
        up to the last 30 days or the 10k most recently created records

        since: must be a UNIX formatted timestamp in milliseconds
        """
        finished = False
        output = []
        querylimit = 100  # max according to the docs

        while not finished:
            params = {
                "count": querylimit,
                "offset": offset,
                "includePropertyVersions": include_versions,
            }
            if since:
                params["since"] = since
            batch = self._call(
                "deal/recent/created",
                method="GET",
                params=params,
                doseq=True,
                **options
            )
            output.extend(
                [
                    prettify(deal, id_key="dealId")
                    for deal in batch["results"]
                    if not deal["isDeleted"]
                ]
            )
            finished = not batch["hasMore"] or len(output) >= limit
            offset = batch["offset"]

        return output[:limit]

    def get_recently_modified(
        self, limit=100, offset=0, since=None, include_versions=False, **options
    ):
        """
        get recently modified deals
        up to the last 30 days or the 10k most recently modified records

        since: must be a UNIX formatted timestamp in milliseconds
        """
        finished = False
        output = []
        querylimit = 100  # max according to the docs

        while not finished:
            params = {
                "count": querylimit,
                "offset": offset,
                "includePropertyVersions": include_versions,
            }
            if since:
                params["since"] = since
            batch = self._call(
                "deal/recent/modified",
                method="GET",
                params=params,
                doseq=True,
                **options
            )
            output.extend(
                [
                    prettify(deal, id_key="dealId")
                    for deal in batch["results"]
                    if not deal["isDeleted"]
                ]
            )
            finished = not batch["hasMore"] or len(output) >= limit
            offset = batch["offset"]

        return output[:limit]
