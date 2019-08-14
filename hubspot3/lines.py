"""
hubspot lines api
"""
from typing import Dict

from hubspot3.crm_associations import CRMAssociationsClient
from hubspot3.base import BaseClient
from hubspot3.utils import get_log


LINES_API_VERSION = "1"


class LinesClient(BaseClient):
    """
    Line Items API endpoint
    THIS API ENDPOINT IS ONLY A PREVIEW AND IS SUBJECT TO CHANGE
    :see: https://developers.hubspot.com/docs/methods/line-items/line-items-overview
    """

    def __init__(self, *args, **kwargs):
        super(LinesClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.lines")

    def _get_path(self, subpath: str):
        return "crm-objects/v{}/objects/line_items/{}".format(
            self.options.get("version") or LINES_API_VERSION, subpath
        )

    def create(self, data=None, **options) -> Dict:
        """
        Create a line item.
        :see: https://developers.hubspot.com/docs/methods/line-items/create-line-item
        """
        return self._call("", data=data, method="POST", **options)

    def delete(self, line_id: int, **options) -> Dict:
        """
        Delete a line item by its ID.
        :see: https://developers.hubspot.com/docs/methods/line-items/delete-line-item
        """
        return self._call("{}".format(line_id), method="DELETE", **options)

    def get(self, line_id: int, **options) -> Dict:
        """
        Retrieve a line by its ID.
        :see: https://developers.hubspot.com/docs/methods/line-items/get_line_item_by_id
        """
        return self._call("{}".format(line_id), **options)

    def link_line_item_to_deal(self, line_item_id, deal_id) -> Dict:
        """Link a line item to a deal."""
        associations_client = CRMAssociationsClient(**self.credentials)
        return associations_client.link_line_item_to_deal(line_item_id, deal_id)
