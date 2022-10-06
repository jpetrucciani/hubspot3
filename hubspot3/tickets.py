"""
hubspot tickets api
"""
from typing import Dict, Iterator, List, Set, Union

from hubspot3.base import BaseClient
from hubspot3.utils import prettify, get_log, join_output_properties, split_properties


TICKETS_API_VERSION = "1"


class TicketsClient(BaseClient):
    """
    hubspot3 Tickets client
    :see: https://developers.hubspot.com/docs/methods/tickets/tickets-overview
    """

    default_batch_properties = ["subject"]

    """
    Since this value is not defined by hubspot, and the tickets API is
    different from the others I won't assume that this number is equal
    for all APIs. Waiting on an anwser from Hubspot for a more precise
    value
    """

    class Recency:
        """recency type enum"""

        CREATED = "CREATED"
        MODIFIED = "CHANGED"
        DELETED = "DELETED"

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

    def get_all(self, limit: int = -1, extra_properties: Union[List[str], str] = None,
                with_history: bool = False, **options) -> list:
        """
        Get all tickets in hubspot
        :see: https://developers.hubspot.com/docs/methods/tickets/get-all-tickets
        """
        generator = self.get_all_as_generator(limit=limit, extra_properties=extra_properties,
                                              with_history=with_history, **options)
        return list(generator)

    def get_all_as_generator(self, limit: int = -1, extra_properties: Union[List[str], str] = None,
                             with_history: bool = False, **options) -> Iterator[dict]:
        """
        Get all tickets in hubspot, returning them as a generator
        :see: https://developers.hubspot.com/docs/methods/tickets/get-all-tickets
        """

        limited = limit > 0

        properties = self._get_properties(extra_properties)

        if with_history:
            property_name = "propertiesWithHistory"
        else:
            property_name = "properties"

        properties_groups = split_properties(properties, property_name=property_name)

        offset = 0
        total_tickets = 0
        finished = False
        while not finished:
            # Since properties is added to the url there is a limiting amount that you can request
            unjoined_outputs = []
            for properties_group in properties_groups:
                batch = self._call(
                    "objects/tickets/paged",
                    method="GET",
                    doseq=True,
                    params={"offset": offset, property_name: properties_group},
                    **options
                )
                unjoined_outputs.extend(batch["objects"])

            outputs = join_output_properties(unjoined_outputs, "objectId")

            total_tickets += len(outputs)
            offset = batch["offset"]

            reached_limit = limited and total_tickets >= limit
            finished = not batch["hasMore"] or reached_limit

            # Since the API doesn't aways tries to return 100 tickets we may pass the desired limit
            if reached_limit:
                outputs = outputs[:limit]

            yield from outputs

    def _get_properties(self, extra_properties: Union[List[str], str] = None) -> Set[str]:
        properties = set(self.default_batch_properties)

        if extra_properties:
            if isinstance(extra_properties, list):
                properties.update(extra_properties)
            if isinstance(extra_properties, str):
                properties.add(extra_properties)

        return properties

    def _get_batch(self, ids: List[int], extra_properties: Union[List[str], str] = None,
                   with_history: bool = False) -> Dict[str, dict]:
        """given a batch of ticket_ids, get more of their info"""
        properties = self._get_properties(extra_properties)
        if with_history:
            property_name = "propertiesWithHistory"
        else:
            property_name = "properties"

        properties_groups = split_properties(properties, property_name=property_name)

        # run the ids as a list of 100
        batch = {}
        remaining_ids = ids.copy()
        while len(remaining_ids) > 0:
            partial_ids = remaining_ids[:100]
            remaining_ids = remaining_ids[100:]

            unjoined_outputs = []
            for properties_group in properties_groups:
                partial_batch = self._call(
                    "objects/tickets/batch-read",
                    method="POST",
                    doseq=True,
                    params={"includeDeletes": True, property_name: properties_group},
                    data={"ids": partial_ids}
                )
                unjoined_outputs.extend(partial_batch.values())

            partial_batch = self._join_output_properties(unjoined_outputs)
            batch.update(partial_batch)
        return batch

    def get_batch(self, ids: List[int],
                  extra_properties: Union[List[str], str] = None) -> List[dict]:
        """given a batch of ticket, get more of their info"""
        batch = self._get_batch(ids, extra_properties=extra_properties, with_history=False)
        return [prettify(batch[ticket_id], id_key="objectId") for ticket_id in batch]

    def get_batch_with_history(self, ids: List[int],
                               extra_properties: Union[List[str], str] = None) -> Dict[str, dict]:
        """given a batch of ticket, get more of their info with history"""
        batch = self._get_batch(ids, extra_properties=extra_properties, with_history=True)
        return batch

    def _get_recent(
        self,
        recency_type: str,
        limit: int = -1,
        ticket_id_offset: int = 0,
        time_offset: int = 0,
        **options
    ) -> List:

        limited = limit > 0
        total_tickets = 0
        finished = False
        while not finished:
            params = {}
            if ticket_id_offset:
                params["objectId"] = ticket_id_offset
            if time_offset:
                params["timestamp"] = int(time_offset)
            params["changeType"] = recency_type
            changes = self._call(
                "change-log/tickets",
                method="GET",
                params=params,
                doseq=True,
                **options
            )
            total_tickets += len(changes)
            finished = (len(changes) == 0) or (limited and total_tickets >= limit)
            if len(changes) > 0:
                ticket_id_offset = changes[-1]["objectId"]
                time_offset = changes[-1]["timestamp"]

            yield from changes

    def get_recently_modified_as_generator(self, limit: int = -1, time_offset: int = 0,
                                           ticket_id_offset: int = 0) -> List[dict]:
        """
        get recently modified and created tickets, the returned value is done with
        yield at each page (max 1000 changes)
        :see: https://developers.hubspot.com/docs/methods/tickets/get-ticket-changes
        """
        return self._get_recent(TicketsClient.Recency.MODIFIED, limit=limit,
                                time_offset=time_offset, ticket_id_offset=ticket_id_offset)

    def get_recently_modified(self, limit: int = -1, time_offset: int = 0,
                              ticket_id_offset: int = 0) -> List[dict]:
        """
        get recently modified and created tickets, returned as a list of all changes
        :see: https://developers.hubspot.com/docs/methods/tickets/get-ticket-changes
        """
        generator = self.get_recently_modified_as_generator(limit=limit, time_offset=time_offset,
                                                            ticket_id_offset=ticket_id_offset)
        return list(generator)

    def get_recently_created_as_generator(self, limit: int = -1, time_offset: int = 0,
                                          ticket_id_offset: int = 0) -> List[dict]:
        """
        get recently created tickets, the returned value is done with yield at each
        page (max 1000 changes)
        :see: https://developers.hubspot.com/docs/methods/tickets/get-ticket-changes
        """
        return self._get_recent(TicketsClient.Recency.CREATED, limit=limit,
                                time_offset=time_offset, ticket_id_offset=ticket_id_offset)

    def get_recently_created(self, limit: int = -1, time_offset: int = 0,
                             ticket_id_offset: int = 0) -> List[dict]:
        """
        get recently created tickets, returned as a list of all changes
        :see: https://developers.hubspot.com/docs/methods/tickets/get-ticket-changes
        """
        generator = self.get_recently_created_as_generator(limit=limit, time_offset=time_offset,
                                                           ticket_id_offset=ticket_id_offset)
        return list(generator)
