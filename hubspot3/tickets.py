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
        max_time_diff_ms: int = 60000,  # Needs a better name,
        # default value waiting for https://community.hubspot.com/t5/APIs-Integrations/Time-difference-between-ticket-s-quot-get-log-of-changes-quot/m-p/297909#M27982
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

            total_tickets += len(batch)
            finished = len(batch) == 0 or (limited and total_tickets >= limit)
            if len(batch) > 0:
                vid_offset = batch[-1]['objectId']
                time_offset = batch[-1]['timestamp']
                changes = self._parse_changes(batch, query_limit, max_time_diff_ms)
                yield changes

    def _parse_changes(self, batch, query_limit, max_time_diff_ms):
        # First lets group changes by deal id
        changes_by_id = [(ticket_change['objectId'], ticket_change) for ticket_change in batch]
        changes_by_id = sorted(changes_by_id, key=itemgetter(0))
        changes_by_id = dict((key, list(value)) for key, value in itertools.groupby(changes_by_id, key=itemgetter(0)))
        # Loop through ids in batches of 100 (limit of the batch API)
        for index in range(int(len(changes_by_id) / query_limit) + 1):
            changes_by_id_batch = dict(list(changes_by_id.items())[index * query_limit:(index + 1) * query_limit])
            properties = []
            for ticket_id, changes in changes_by_id_batch.items():
                for ticket_id, change in changes:
                    properties += change['changes']['changedProperties']
            properties = set(properties)
            # Get the information of each change
            tickets_history = self.get_batch(list(changes_by_id_batch.keys()),
                                             extra_properties=list(properties))
            for ticket_id, ticket_history in tickets_history.items():
                ticket_id = int(ticket_id)
                properties = ticket_history['properties']
                # Match the information of changes with each change
                changes = changes_by_id_batch[ticket_id]
                for ticket_id, change in changes:
                    change['changes']['changedValues'] = {}
                    for changed_variable in change['changes']['changedProperties']:
                        versions = properties[changed_variable]['versions']
                        time_diffs = [abs(version['timestamp'] - change['timestamp'])
                                      for version in versions]
                        min_time_index = min(range(len(time_diffs)),
                                             key=time_diffs.__getitem__)
                        if time_diffs[min_time_index] <= max_time_diff_ms:
                            value = versions[min_time_index]['value']
                            change['changes']['changedValues'][changed_variable] = value
                        else:
                            get_log.warning(f"Unable to find value for {changed_variable}"
                                            " within the time range")
        # Finally lets return only the changes as a list
        return [change[1] for changes in changes_by_id.values() for change in changes]

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
