"""
hubspot tickets api
"""
from hubspot3 import logging_helper
from hubspot3.base import BaseClient


TICKETS_API_VERSION = "1"


class TicketsClient(BaseClient):
    """
    hubspot3 Tickets client
    this client is still in developer preview, and is subject to change.
    :see: https://developers.hubspot.com/docs/methods/tickets/tickets-overview
    """

    def __init__(self, *args, **kwargs):
        """initialize a tickets client"""
        super(TicketsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.tickets")

    def _get_path(self, subpath):
        """tickets subpath generator"""
        return "crm-objects/v{}/{}".format(TICKETS_API_VERSION, subpath)

    def create(self, pipeline: str, stage: str, properties: dict = None, **options) -> dict:
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

    def get(self, ticket_id: str, include_deleted: bool = False, **options) -> dict:
        """
        get a ticket by its ticket_id
        TODO: add properties support
        :see: https://developers.hubspot.com/docs/methods/tickets/get_ticket_by_id
        """
        params = {"includeDeletes": include_deleted}

        return self._call("objects/tickets/{}".format(ticket_id), params=params, **options)

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
                "objects/tickets/paged", method="GET", params={"offset": offset}, **options
            )
            output.extend(batch["objects"])
            finished = not batch["hasMore"]
            offset = batch["offset"]

        return output if not limited else output[:limit]
