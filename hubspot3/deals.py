"""
hubspot deals api
"""
import urllib.parse
from typing import Dict, Union, List

from hubspot3.base import BaseClient
from hubspot3.utils import get_log, prettify, split_properties

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
        return "deals/v{}/{}".format(
            self.options.get("version") or DEALS_API_VERSION, subpath
        )

    def get(self, deal_id: str, **options):
        return self._call("deal/{}".format(deal_id), method="GET", **options)

    def create(self, data: dict = None, **options):
        """
        create deal api call
        :see: https://developers.hubspot.com/docs/methods/deals/create_deal
        """
        data = data or {}
        return self._call("deal/", data=data, method="POST", **options)

    def update(self, deal_id: str, data: dict = None, **options):
        data = data or {}
        return self._call("deal/{}".format(deal_id), data=data, method="PUT", **options)

    def delete(self, deal_id: str, **options) -> Dict:
        """
        Delete a deal.
        :see: https://developers.hubspot.com/docs/methods/deals/delete_deal
        """
        return self._call("deal/{}".format(deal_id), method="DELETE", **options)

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

    def get_all(
        self,
        offset: int = 0,
        extra_properties: Union[list, str] = None,
        limit: int = -1,
        **options
    ):
        deals_generator = self.get_all_as_generator(offset=offset,
                                                    extra_properties=extra_properties,
                                                    limit=limit, with_history=False, **options)
        deals = list(deals_generator)
        pretty_deals = [prettify(deal, id_key="dealId") for deal in deals if not deal["isDeleted"]]
        return pretty_deals

    def _join_output_properties(self, deals: List[dict]) -> dict:
        """
        Join request properties to show only one object per ticketId
        This will change the first object for each ticketId
        """
        joined_deals_dict = {}
        for deal in deals:
            # Converting the ID to str to make it compatible with API
            deal_id = str(deal["dealId"])
            if deal_id not in joined_deals_dict:
                joined_deals_dict[deal_id] = deal
            else:
                joined_deals_dict[deal_id]["properties"].update(deal["properties"])
        joined_deals = list(joined_deals_dict.values())
        return joined_deals

    def get_all_as_generator(
        self,
        offset: int = 0,
        extra_properties: Union[list, str] = None,
        limit: int = -1,
        with_history: bool = False,
        **options
    ):
        """
        get all deals in the hubspot account.
        extra_properties: a list used to extend the properties fetched
        :see: https://developers.hubspot.com/docs/methods/deals/get-all-deals
        """
        if with_history:
            property_name = "propertiesWithHistory"
        else:
            property_name = "properties"
        finished = False
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

        properties_groups = split_properties(properties, property_name=property_name)
        deal_counter = 0
        while not finished:
            unjoined_deals = []
            for properties_group in properties_groups:
                batch = self._call(
                    "deal/paged",
                    method="GET",
                    params={
                        "limit": query_limit,
                        "offset": offset,
                        property_name: properties_group,
                        "includeAssociations": True,
                    },
                    doseq=True,
                    **options
                )
                unjoined_deals.extend(batch["deals"])

            deals = self._join_output_properties(unjoined_deals)

            deal_counter += len(deals)
            reached_limit = limited and deal_counter >= limit

            if reached_limit:
                cutoff = len(deals) - (deal_counter - limit)
                deals = deals[:cutoff]

            finished = not batch["hasMore"] or reached_limit
            offset = batch["offset"]

            yield from deals

    def _get_recent(
        self,
        recency_type: str,
        limit: int = 100,
        offset: int = 0,
        since: int = None,
        include_versions: bool = False,
        **options
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
                "deal/recent/{}".format(recency_type),
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

    def get_recently_created(
        self,
        limit: int = 100,
        offset: int = 0,
        since: int = None,
        include_versions: bool = False,
        **options
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
            **options
        )

    def get_recently_modified(
        self,
        limit: int = 100,
        offset: int = 0,
        since: int = None,
        include_versions: bool = False,
        **options
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
            **options
        )
