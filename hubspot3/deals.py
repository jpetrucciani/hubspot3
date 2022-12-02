"""
hubspot deals api
"""
import urllib.parse
from typing import Dict, Optional, Union
from hubspot3.base import BaseClient
from hubspot3.utils import get_log, prettify


DEALS_API_VERSION = "1"


class DealsClient(BaseClient):
    """
    The hubspot3 Deals client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json returned
    """

    class Recency:
        """recency type enum"""

        CREATED = "created"
        MODIFIED = "modified"

    def __init__(self, *args, **kwargs):
        super(DealsClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.deals")

    def _get_path(self, subpath):
        """get the full api url for the given subpath on this client"""
        return f"deals/v{self.options.get('version') or DEALS_API_VERSION}/{subpath}"

    def get(self, deal_id: str, **options):
        """
        get a single deal by id
        :see: https://developers.hubspot.com/docs/methods/deals/get_deal
        """
        return self._call(f"deal/{deal_id}", method="GET", **options)

    def create(self, data: Optional[Dict] = None, **options):
        """
        create deal api call
        :see: https://developers.hubspot.com/docs/methods/deals/create_deal
        """
        data = data or {}
        return self._call("deal/", data=data, method="POST", **options)

    def update(self, deal_id: str, data: Optional[Dict] = None, **options):
        """
        update a deal by id
        :see: https://developers.hubspot.com/docs/methods/deals/update_deal
        """
        data = data or {}
        return self._call(f"deal/{deal_id}", data=data, method="PUT", **options)

    def delete(self, deal_id: str, **options) -> Dict:
        """
        Delete a deal.
        :see: https://developers.hubspot.com/docs/methods/deals/delete_deal
        """
        return self._call(f"deal/{deal_id}", method="DELETE", **options)

    def associate(self, deal_id, object_type, object_ids, **options):
        # Encoding the query string here since HubSpot is expecting the "id" parameter to be
        # repeated for each object ID, which is not a standard practice and
        # won't work otherwise.
        object_ids = [("id", object_id) for object_id in object_ids]
        query = urllib.parse.urlencode(object_ids)

        return self._call(
            f"deal/{deal_id}/associations/{object_type}",
            method="PUT",
            query=query,
            **options,
        )

    def get_all(
        self,
        offset: int = 0,
        extra_properties: Union[list, str, None] = None,
        limit: int = -1,
        **options,
    ):
        """
        get all deals in the hubspot account.
        extra_properties: a list used to extend the properties fetched
        :see: https://developers.hubspot.com/docs/methods/deals/get-all-deals
        """
        finished = False
        output = []
        query_limit = 250  # Max value according to docs
        limited = limit > 0
        if limited and limit < query_limit:
            query_limit = limit

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
                    "limit": query_limit,
                    "offset": offset,
                    "properties": properties,
                    "includeAssociations": True,
                },
                doseq=True,
                **options,
            )
            output.extend(
                [
                    prettify(deal, id_key="dealId")
                    for deal in batch["deals"]
                    if not deal["isDeleted"]
                ]
            )
            finished = not batch["hasMore"] or (limited and len(output) >= limit)
            offset = batch["offset"]

        return output if not limited else output[:limit]

    def _get_recent(
        self,
        recency_type: str,
        limit: int = 100,
        offset: int = 0,
        since: Optional[int] = None,
        include_versions: bool = False,
        **options,
    ):
        """
        returns a list of either recently created or recently modified deals

        :param since: unix formatted timestamp in milliseconds
        """
        finished = False
        output = []
        query_limit = 100  # max according to the docs
        limited = limit > 0
        if limited and limit < query_limit:
            query_limit = limit

        while not finished:
            params = {
                "count": query_limit,
                "offset": offset,
                "includePropertyVersions": include_versions,
            }
            if since:
                params["since"] = since
            batch = self._call(
                f"deal/recent/{recency_type}",
                method="GET",
                params=params,
                doseq=True,
                **options,
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

    def get_recently_created(
        self,
        limit: int = 100,
        offset: int = 0,
        since: Optional[int] = None,
        include_versions: bool = False,
        **options,
    ):
        """
        get recently created deals
        up to the last 30 days or the 10k most recently created records

        since: must be a UNIX formatted timestamp in milliseconds
        """
        return self._get_recent(
            DealsClient.Recency.CREATED,
            limit=limit,
            offset=offset,
            since=since,
            include_versions=include_versions,
            **options,
        )

    def get_recently_modified(
        self,
        limit: int = 100,
        offset: int = 0,
        since: Optional[int] = None,
        include_versions: bool = False,
        **options,
    ):
        """
        get recently modified deals
        up to the last 30 days or the 10k most recently modified records

        since: must be a UNIX formatted timestamp in milliseconds
        """
        return self._get_recent(
            DealsClient.Recency.MODIFIED,
            limit=limit,
            offset=offset,
            since=since,
            include_versions=include_versions,
            **options,
        )
