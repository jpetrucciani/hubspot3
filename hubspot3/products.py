"""
hubspot products api
"""
from hubspot3.base import BaseClient
from hubspot3.utils import prettify, get_log, ordered_dict
from typing import Dict, List, Optional


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

    def get_product(
        self, product_id: str, properties: Optional[List[str]] = None, **options
    ):
        """get single product based on product ID in the hubspot account"""
        properties = properties or []
        return self._call(
            f"objects/products/{product_id}",
            method="GET",
            params={"properties": ["name", "description", *properties]},
            doseq=True,
            **options,
        )

    def get_all_products(
        self, properties: Optional[List[str]] = None, offset: int = 0, **options
    ):
        """get all products in the hubspot account"""
        properties = properties or []
        finished = False
        output = []
        querylimit = 100  # Max value according to docs
        while not finished:
            batch = self._call(
                "objects/products/paged",
                method="GET",
                params=ordered_dict(
                    {
                        "limit": querylimit,
                        "offset": offset,
                        "properties": ["name", "description", *properties],
                    }
                ),
                doseq=True,
                **options,
            )
            output.extend(
                [
                    prettify(obj, id_key="objectId")
                    for obj in batch["objects"]
                    if not obj["isDeleted"]
                ]
            )
            finished = not batch["hasMore"]
            offset = batch["offset"]

        return output

    def _get_path(self, subpath: str):
        return f"crm-objects/v{self.options.get('version') or PRODUCTS_API_VERSION}/{subpath}"

    def create(self, data: Optional[Dict] = None, **options):
        """Create a new product."""
        data = data or {}
        return self._call("objects/products", data=data, method="POST", **options)

    def update(self, product_id: str, data: Optional[Dict] = None, **options):
        """Update a product based on its product ID."""
        data = data or {}
        return self._call(
            f"objects/products/{product_id}", data=data, method="PUT", **options
        )

    def delete(self, product_id: str, **options):
        """Delete a product based on its product ID."""
        return self._call(f"objects/products/{product_id}", method="DELETE", **options)
