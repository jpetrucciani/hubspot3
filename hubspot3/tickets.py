"""
hubspot tickets api
"""
from typing import Dict, Iterator, List, Set, Union

from hubspot3.base import BaseClient
from hubspot3.utils import prettify, get_log


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
    _MAXIMUM_REQUEST_LENGTH = 15500

    """
    Same comment above is true for this
    """
    _MAX_TIME_DIFF_MS = 60000

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

    def _join_output_properties(self, tickets: List[dict]) -> List[dict]:
        """
        Join request properties to show only one output per ticketId
        This will change the first object for each ticketId
        """
        joined_tickets_dict = {}
        for ticket in tickets:
            ticket_id = ticket["objectId"]
            if ticket_id not in joined_tickets_dict:
                joined_tickets_dict[ticket_id] = ticket
            else:
                joined_tickets_dict[ticket_id]["properties"].update(ticket["properties"])
        return list(joined_tickets_dict.values())

    def _split_properties(self, properties: Set[str],
                          max_properties_request_length: int = None,
                          property_name: str = "properties") -> List[Set[str]]:
        """
        Split a set of properties in a list of sets of properties where the total length of
        "properties=..." for each property is smaller than the max
        """
        if max_properties_request_length is None:
            max_properties_request_length = self._MAXIMUM_REQUEST_LENGTH

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

        properties_groups = self._split_properties(properties, property_name=property_name)

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
            outputs = self._join_output_properties(unjoined_outputs)

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
        params = {}
        params[property_name] = list(properties)
        params["includeDeletes"] = True
        # run the ids as a list of 100
        batch = {}
        remaining_ids = ids.copy()
        while len(remaining_ids) > 0:
            partial_ids = remaining_ids[:100]
            remaining_ids = remaining_ids[100:]
            partial_batch = self._call(
                "objects/tickets/batch-read",
                method="POST",
                doseq=True,
                params=params,
                data={"ids": partial_ids}
            )
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
        max_time_diff_ms: int = None,
        **options
    ) -> List:

        if max_time_diff_ms is None:
            max_time_diff_ms = self._MAX_TIME_DIFF_MS

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

                ids = {change["objectId"] for change in changes}
                properties = []
                for change in changes:
                    if change["changeType"] != TicketsClient.Recency.DELETED:
                        properties.extend(change["changes"]["changedProperties"])
                properties = set(properties)

                # This is an getting all the changed variables for all tickets,
                # this is more data than needed, should eventually break in
                # groups to get less discarted data
                tickets_history = self.get_batch_with_history(list(ids),
                                                              extra_properties=list(properties))

                changes = self._merge_changes_with_history(changes, tickets_history,
                                                           max_time_diff_ms)
                yield from changes

    def _merge_changes_with_history(self,
                                    changes: list,
                                    tickets_history: dict,
                                    max_time_diff_ms: int) -> List[dict]:
        # First lets group changes by deal id
        changes_by_id = {}
        for change in changes:
            change_id = change["objectId"]
            if change_id not in changes_by_id:
                changes_by_id[change_id] = []
            changes_by_id[change_id].append(change)

        # Now merge
        for ticket_id, ticket_history in tickets_history.items():
            ticket_id = int(ticket_id)
            properties = ticket_history["properties"]
            # Match the information of changes with each change
            changes = changes_by_id[ticket_id]
            for change in changes:
                if change["changeType"] == TicketsClient.Recency.DELETED:
                    # Deleted changes have no properties
                    continue
                change["changes"]["changedValues"] = {}
                for changed_variable in change["changes"]["changedProperties"]:
                    versions = properties[changed_variable]["versions"]
                    # Get the smallest time diff between change and history
                    time_diffs = [abs(version["timestamp"] - change["timestamp"])
                                  for version in versions]
                    min_time_index = min(range(len(time_diffs)),
                                         key=time_diffs.__getitem__)
                    if time_diffs[min_time_index] <= max_time_diff_ms:
                        if "value" in versions[min_time_index]:
                            value = versions[min_time_index]["value"]
                        else:
                            value = None
                        change["changes"]["changedValues"][changed_variable] = value
                    else:
                        get_log(__name__).warning("Unable to find value for "
                                                  "{}".format(changed_variable)
                                                  + " within the time range for ticket"
                                                  " {}".format(ticket_id))
        # Finally lets return only the changes as a list
        return [change for changes in changes_by_id.values() for change in changes]

    def get_recently_modified_as_generator(self, limit: int = -1, time_offset: int = 0,
                                           ticket_id_offset: int = 0) -> List[dict]:
        """
        get recently modified and created tickets, adding a field in changes-changedValue with
        the value of each change
        the returned value is done with yield at each page (max 1000 changes)
        :see: https://developers.hubspot.com/docs/methods/tickets/get-ticket-changes
        """
        return self._get_recent(TicketsClient.Recency.MODIFIED, limit=limit,
                                time_offset=time_offset, ticket_id_offset=ticket_id_offset)

    def get_recently_modified(self, limit: int = -1, time_offset: int = 0,
                              ticket_id_offset: int = 0) -> List[dict]:
        """
        get recently modified and created tickets, adding a field in changes-changedValue with
        the value of each change
        returned as a list of all changes
        :see: https://developers.hubspot.com/docs/methods/tickets/get-ticket-changes
        """
        generator = self.get_recently_modified_as_generator(limit=limit, time_offset=time_offset,
                                                            ticket_id_offset=ticket_id_offset)
        return list(generator)

    def get_recently_created_as_generator(self, limit: int = -1, time_offset: int = 0,
                                          ticket_id_offset: int = 0) -> List[dict]:
        """
        get recently created tickets, adding a field in changes-changedValue with
        the value of each change
        the returned value is done with yield at each page (max 1000 changes)
        :see: https://developers.hubspot.com/docs/methods/tickets/get-ticket-changes
        """
        return self._get_recent(TicketsClient.Recency.CREATED, limit=limit,
                                time_offset=time_offset, ticket_id_offset=ticket_id_offset)

    def get_recently_created(self, limit: int = -1, time_offset: int = 0,
                             ticket_id_offset: int = 0) -> List[dict]:
        """
        get recently created tickets, adding a field in changes-changedValue with
        the value of each change
        returned as a list of all changes
        :see: https://developers.hubspot.com/docs/methods/tickets/get-ticket-changes
        """
        generator = self.get_recently_created_as_generator(limit=limit, time_offset=time_offset,
                                                           ticket_id_offset=ticket_id_offset)
        return list(generator)
