"""
hubspot lines api
"""
from hubspot3.base import BaseClient
from hubspot3.crm_associations import CRMAssociationsClient
from hubspot3.utils import get_log, join_output_properties, ordered_dict, prettify
from typing import Dict, Iterator, List, Union


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
    
    def get_all(self, limit: int = -1, extra_properties: Union[List[str], str] = None,
                with_history: bool = False, **options) -> list:
        """
        Get all line items in hubspot
        :see: https://legacydocs.hubspot.com/docs/methods/line-items/get-all-line-items
        """
        generator = self.get_all_as_generator(limit=limit, extra_properties=extra_properties,
                                              with_history=with_history, **options)
        return list(generator)
    
    def get_all_as_generator(self, limit: int = -1, extra_properties: Union[List[str], str] = None,
                             with_history: bool = False, **options) -> Iterator[dict]:
        """
        Get all line items in hubspot
        :see: https://legacydocs.hubspot.com/docs/methods/line-items/get-all-line-items
        """

        limited = limit > 0

        properties = extra_properties

        if with_history:
            property_name = "propertiesWithHistory"
        else:
            property_name = "properties"

        properties_groups = split_properties(properties, property_name=property_name)

        offset = 0
        total_line_items = 0
        finished = False
        while not finished:
            # Since properties is added to the url there is a limiting amount that you can request
            unjoined_outputs = []
            for properties_group in properties_groups:
                batch = self._call(
                    "objects/line_items/paged",
                    method="GET",
                    doseq=True,
                    params={"offset": offset, property_name: properties_group},
                    **options
                )
                unjoined_outputs.extend(batch["objects"])

            outputs = join_output_properties(unjoined_outputs, "objectId")

            total_line_items += len(outputs)
            offset = batch["offset"]

            reached_limit = limited and total_line_items>= limit
            finished = not batch["hasMore"] or reached_limit

            # Since the API doesn't aways tries to return 100 line items we may pass the desired limit
            if reached_limit:
                outputs = outputs[:limit]

            yield from outputs

    def link_line_item_to_deal(self, line_item_id, deal_id) -> Dict:
        """Link a line item to a deal."""
        associations_client = CRMAssociationsClient(**self.credentials)
        return associations_client.link_line_item_to_deal(line_item_id, deal_id)
