"""
hubspot tickets api
"""
from typing import Dict, List, Optional
from hubspot3.base import BaseClient
from hubspot3.utils import get_log


TICKETS_API_VERSION = "1"


class TicketsClient(BaseClient):
    """
    hubspot3 Tickets client
    :see: https://developers.hubspot.com/docs/methods/tickets/tickets-overview
    """

    def __init__(self, *args, **kwargs):
        """initialize a tickets client"""
        super(TicketsClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.tickets")

    def _get_path(self, subpath):
        """tickets subpath generator"""
        return f"crm-objects/v{TICKETS_API_VERSION}/{subpath}"

    def create(
        self, pipeline: str, stage: str, properties: Optional[Dict] = None, **options
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

    def update(self, ticket_id: str, data: Dict, **options) -> Dict:
        """
        update a ticket by its ticket id, with the given data
        :see: https://developers.hubspot.com/docs/methods/tickets/update-ticket
        """
        ticket_data = [{"name": x, "value": y} for x, y in data.items()]
        return self._call(
            f"objects/tickets/{ticket_id}", method="PUT", data=ticket_data, **options
        )

    def get(
        self,
        ticket_id: str,
        properties: Optional[List[str]] = None,
        include_deleted: bool = False,
        **options,
    ) -> Dict:
        """
        get a ticket by its ticket_id
        :see: https://developers.hubspot.com/docs/methods/tickets/get_ticket_by_id
        """
        properties = properties or [
            "subject",
            "content",
            "hs_pipeline",
            "hs_pipeline_stage",
        ]

        params = options.pop("params", {})
        params.update({"includeDeletes": include_deleted})
        options.update({"params": params})

        return self._call(
            f"objects/tickets/{ticket_id}",
            method="GET",
            properties=properties,
            **options,
        )

    def get_all(
        self, properties: Optional[List[str]] = None, limit: int = -1, **options
    ) -> list:
        """
        Get all tickets in hubspot
        :see: https://developers.hubspot.com/docs/methods/tickets/get-all-tickets
        """
        properties = properties or [
            "subject",
            "content",
            "hs_pipeline",
            "hs_pipeline_stage",
        ]

        finished = False
        output = []  # type: list
        offset = 0
        limited = limit > 0
        while not finished:
            batch = self._call(
                "objects/tickets/paged",
                method="GET",
                params={"offset": offset},
                properties=properties,
                **options,
            )
            output.extend(batch["objects"])
            finished = not batch["hasMore"]
            offset = batch["offset"]

        return output if not limited else output[:limit]
