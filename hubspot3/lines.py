"""
hubspot lines api
"""
from typing import Dict, Union
from hubspot3.base import BaseClient
from hubspot3.crm_associations import CRMAssociationsClient
from hubspot3.utils import get_log, prettify, ordered_dict


LINES_API_VERSION = "1"


class LinesClient(BaseClient):
    """
    Line Items API endpoint
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

    def update(self, line_id: int, data=None, **options) -> Dict:
        """
        Update an existing line by its ID.
        :see: https://developers.hubspot.com/docs/methods/line-items/update-line-item
        """
        data = data or {}
        return self._call("{}".format(line_id), data=data, method="PUT", **options)

    def get_all(
        self,
        offset: int = 0,
        extra_properties: Union[list, str] = None,
        limit: int = -1,
        **options
    ):
        """
        Retrieve all the line items in the Hubspot account.

        Cf: https://developers.hubspot.com/docs/methods/line-items/get-all-line-items

        :param offset Used to get the next set of results.
        :param extra_properties By default, only the ID, the hubspot product id (`hs_product_id`)
        a few other system fields are returned for the line items. This method with also ask for
        basic properties such as the 'name', the 'price' and the 'quantity'. More could be
        retrieved by using 'extra_properties'.
        :param limit: could be used to prevent to fetch the entire results. Default value is `-1`,
        meaning unlimited.
        """
        finished = False
        output = []
        limited = limit > 0

        # Default properties to fetch
        properties = ["name", "price", "quantity"]

        # append extras if they exist
        if extra_properties:
            if isinstance(extra_properties, list):
                properties += extra_properties
            if isinstance(extra_properties, str):
                properties.append(extra_properties)

        while not finished:
            batch = self._call(
                "paged",
                method="GET",
                params=ordered_dict({"offset": offset, "properties": properties}),
                doseq=True,
                **options
            )
            output.extend(
                [
                    prettify(line_item, id_key="objectId")
                    for line_item in batch["objects"]
                    if not line_item["isDeleted"]
                ]
            )
            finished = not batch["hasMore"] or (limited and len(output) >= limit)
            offset = batch["offset"]

        return output if not limited else output[:limit]

    def link_line_item_to_deal(self, line_item_id, deal_id) -> Dict:
        """Link a line item to a deal."""
        associations_client = CRMAssociationsClient(**self.credentials)
        return associations_client.link_line_item_to_deal(line_item_id, deal_id)
