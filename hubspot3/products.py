"""
hubspot products api
"""
from hubspot3.base import BaseClient
from hubspot3.utils import get_log, ordered_dict, prettify, split_properties
from typing import List


PRODUCTS_API_VERSION = "1"


class ProductsClient(BaseClient):
    """
    Products extension for products API endpoint
    :see: https://developers.hubspot.com/docs/methods/products/products-overview
    """

    def __init__(self, *args, **kwargs) -> None:
        """initialize a products client"""
        super(ProductsClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.products")

    def get_product(self, product_id: str, properties: List[str] = None, **options):
        """get single product based on product ID in the hubspot account"""
        properties = properties or []
        return self._call(
            "objects/products/{product_id}".format(product_id=product_id),
            method="GET",
            params={"properties": ["name", "description", *properties]},
            doseq=True,
            **options
        )
    
    def _join_output_properties(self, products: List[dict]) -> dict:
        """
        Join request properties to show only one object per productId
        This will change the first object for each productId
        """
        joined_products_dict = {}
        for product in products:
            # Converting the ID to str to make it compatible with API
            product_id = str(product["objectId"])
            if product_id not in joined_products_dict:
                joined_products_dict[product_id] = product
            else:
                joined_products_dict[product_id]["properties"].update(product["properties"])
        return joined_products_dict

    def get_all(self, limit: int = -1, extra_properties: Union[List[str], str] = None,
                with_history: bool = False, **options) -> list:
        """
        Get all products in hubspot
        :see: https://developers.hubspot.com/docs/methods/products/get-all-products
        """
        generator = self.get_all_as_generator(limit=limit, extra_properties=extra_properties,
                                              with_history=with_history, **options)
        return list(generator)
    
    def get_all_as_generator(self, limit: int = -1, extra_properties: Union[List[str], str] = None,
                             with_history: bool = False, **options) -> Iterator[dict]:
        """
        Get all products in hubspot
        :see: https://developers.hubspot.com/docs/methods/products/get-all-products
        """

        limited = limit > 0

        properties = extra_properties

        if with_history:
            property_name = "propertiesWithHistory"
        else:
            property_name = "properties"

        properties_groups = split_properties(properties, property_name=property_name)

        offset = 0
        total_products = 0
        finished = False
        while not finished:
            # Since properties is added to the url there is a limiting amount that you can request
            unjoined_outputs = []
            for properties_group in properties_groups:
                batch = self._call(
                    "objects/products/paged",
                    method="GET",
                    doseq=True,
                    params={"offset": offset, property_name: properties_group},
                    **options
                )
                unjoined_outputs.extend(batch["objects"])

            outputs_dict = self._join_output_properties(unjoined_outputs)
            outputs = list(outputs_dict.values())

            total_products += len(outputs)
            offset = batch["offset"]

            reached_limit = limited and total_products>= limit
            finished = not batch["hasMore"] or reached_limit

            # Since the API doesn't aways tries to return 100 products we may pass the desired limit
            if reached_limit:
                outputs = outputs[:limit]

            yield from outputs   

    def _get_path(self, subpath: str):
        return "crm-objects/v{}/{}".format(
            self.options.get("version") or PRODUCTS_API_VERSION, subpath
        )

    def create(self, data=None, **options):
        """Create a new product."""
        data = data or {}
        return self._call("objects/products", data=data, method="POST", **options)

    def update(self, product_id, data=None, **options):
        """Update a product based on its product ID."""
        data = data or {}
        return self._call(
            "objects/products/{product_id}".format(product_id=product_id),
            data=data,
            method="PUT",
            **options
        )

    def delete(self, product_id, **options):
        """Delete a product based on its product ID."""
        return self._call(
            "objects/products/{product_id}".format(product_id=product_id),
            method="DELETE",
            **options
        )
