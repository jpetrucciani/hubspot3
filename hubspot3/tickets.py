"""
hubspot tickets api
"""
from hubspot3 import logging_helper
from hubspot3.base import BaseClient
from hubspot3.utils import prettify
from typing import Union


TICKETS_API_VERSION = "1"


class TicketsClient(BaseClient):
    """
    The hubspot3 Tickets client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        """initialize a tickets client"""
        super(TicketsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.tickets")

    def _get_path(self, subpath):
        return "crm-objects/v{}/{}".format(TICKETS_API_VERSION, subpath)

    def create(self, data=None, **options):
        """create a ticket."""
        data = data or {}
        return self._call(
            "objects/tickets",
            data=data,
            method="POST",
            **options
        )

    def get_all(self, **options):
        """
        Get all tickets in hubspot
        :see: https://developers.hubspot.com/docs/methods/tickets/get-all-tickets
        """

        return self._call(
            "objects/tickets/paged",
            method="GET",
            params={"count": query_limit, "vidOffset": offset},
            **options
        )

