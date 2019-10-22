"""
hubspot tickets api
"""
import itertools
from operator import itemgetter

from hubspot3.base import BaseClient
from hubspot3.utils import prettify, get_log

from typing import Dict
from typing import Union


TICKETS_API_VERSION = "1"


class TicketsClient(BaseClient):
    """
    hubspot3 Tickets client
    :see: https://developers.hubspot.com/docs/methods/tickets/tickets-overview
    """

    class Recency:
        """recency type enum"""

        CREATED = "CREATED"
        MODIFIED = "CHANGED"

    def __init__(self, *args, **kwargs):
        """initialize a tickets client"""
        super(TicketsClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.tickets")

    def _get_path(self, subpath):
        """tickets subpath generator"""
        return "crm-objects/v{}/{}".format(TICKETS_API_VERSION, subpath)

    def create(
        self, pipeline: str, stage: str, properties: dict = None, **options
    ) -> Dict:
        """
        create a ticket.
        pass in a pipeline and stage, then a key value pair of other properties
        properties will be converted to the name=, value=, format automatically
        :see: https://developers.hubspot.com/docs/methods/tickets/create-ticket
        """
        if not pipeline or not stage:
            raise Exception("pipeline and stage are required to create a ticket!")
        if not properties:
            properties = {}
        ticket_data = [{"name": x, "value": y} for x, y in properties.items()]
        ticket_data.append({"name": "hs_pipeline", "value": pipeline})
        ticket_data.append({"name": "hs_pipeline_stage", "value": stage})
        return self._call("objects/tickets", data=ticket_data, method="POST", **options)

    def get(self, ticket_id: str, include_deleted: bool = False, **options) -> Dict:
        """
        get a ticket by its ticket_id
        TODO: add properties support
        :see: https://developers.hubspot.com/docs/methods/tickets/get_ticket_by_id
        """

        params = options.pop("params", {})
        params.update({"includeDeletes": include_deleted})
        options.update({"params": params})

        return self._call(
            "objects/tickets/{}".format(ticket_id), method="GET", **options
        )

    def get_all(self, limit: int = -1, **options) -> list:
        """
        Get all tickets in hubspot
        :see: https://developers.hubspot.com/docs/methods/tickets/get-all-tickets
        """
        finished = False
        output = []  # type: list
        offset = 0
        limited = limit > 0
        while not finished:
            batch = self._call(
                "objects/tickets/paged",
                method="GET",
                params={"offset": offset},
                **options
            )
            output.extend(batch["objects"])
            finished = not batch["hasMore"]
            offset = batch["offset"]

        return output if not limited else output[:limit]

    def get_batch(self, ids, extra_properties: Union[list, str] = None, with_history: bool = False):
        """given a batch of vids, get more of their info"""
        # default properties to fetch
        properties = set([])

        # append extras if they exist
        if extra_properties:
            if isinstance(extra_properties, list):
                properties.update(extra_properties)
            if isinstance(extra_properties, str):
                properties.add(extra_properties)
        if with_history:
            property_name = 'propertiesWithHistory'
        else:
            property_name = 'properties'
        batch = self._call(
            "objects/tickets/batch-read",
            method="POST",
            doseq=True,
            params={property_name: list(properties)},
            data={'ids': ids}
        )
        # It returns a dict with IDs as keys
        return batch

    def _get_recent(
        self,
        recency_type: str,
        limit: int = -1,
        vid_offset: int = 0,
        time_offset: int = 0,
        **options
    ):
        finished = False
        query_limit = 100  # max according to the docs
        recency_string = (
            "all"
            if recency_type == TicketsClient.Recency.CREATED
            else "recently_updated"
        )
        limited = limit > 0
        if limited and limit < query_limit:
            query_limit = limit
        total_tickets = 0
        while not finished:
            params = {"count": query_limit}
            if vid_offset:
                params["objectId"] = vid_offset
            if time_offset:
                params["timestamp"] = int(time_offset)
            params['changeType'] = recency_type
            batch = self._call(
                "change-log/tickets".format(recency_string),
                method="GET",
                params=params,
                doseq=True,
                **options
            )
            ids = [ticket["objectId"] for ticket in batch]
            properties = set([change for ticket in batch for change in
                              ticket['changes']['changedProperties']])
            total_tickets += len(batch)
            finished = len(batch) == 0 or (limited and total_tickets >= limit)
            if len(batch) > 0:
                vid_offset = batch[-1]['objectId']
                time_offset = batch[-1]['timestamp']
                # Rearenge ids in set of 100 (limit of the batch API)
                ids = [[ticket_id for ticket_id in ids[index * query_limit:(index + 1)
                                                       * query_limit]] for index in
                       range(int(len(ids) / query_limit) + 1)]
                output_par = []
                for ids_set in ids:
                    output_par += self.get_batch(ids_set, extra_properties=list(properties))
                yield output_par

    def get_recently_modified_as_generator(self, limit: int = -1, time_offset: int = 0):
        """
        get recently modified and created contacts
        :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_updated_contacts
        """
        return self._get_recent(TicketsClient.Recency.MODIFIED, limit=limit,
                                time_offset=time_offset)

    def get_recently_modified(self, limit: int = -1, time_offset: int = 0):
        """
        get recently modified and created contacts
        :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_updated_contacts
        """
        generator = self.get_recently_modified_as_generator(limit=limit, time_offset=time_offset)
        return list(itertools.chain.from_iterable(generator))
