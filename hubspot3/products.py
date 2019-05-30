"""
hubspot products api
"""
from .base import BaseClient
from .utils import prettify
from . import logging_helper
from typing import List


PRODUCTS_API_VERSION = '1'


class ProductsClient(BaseClient):
    """
    Products extension for products API endpoint
    THIS API ENDPOINT IS ONLY A PREVIEW AND IS SUBJECT TO CHANGE
    see: https://developers.hubspot.com/docs/methods/products/products-overview
    """
    def __init__(self, *args, **kwargs):
        super(ProductsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.companies")

    def get_product(self, product_id: str, properties: List[str] = None, **options):
        """get single product based on product ID in the hubspot account"""
        properties = properties or []
        return self._call(
            f'objects/products/{product_id}',
            method='GET',
            params={
                'properties': [
                    'name',
                    'description',
                    *properties
                ]
            },
            doseq=True,
            **options
        )

    def get_all_products(self, properties: List[str] = None, offset: int = 0, **options):
        """get all products in the hubspot account"""
        properties = properties or []
        finished = False
        output = []
        querylimit = 100  # Max value according to docs
        while not finished:
            batch = self._call(
                'objects/products/paged',
                method='GET',
                params={
                    'limit': querylimit,
                    'offset': offset,
                    'properties': [
                        'name',
                        'description',
                        *properties
                    ]
                },
                doseq=True,
                **options
            )
            output.extend([
                prettify(obj, id_key='objectId')
                for obj in batch['objects']
                if not obj['isDeleted']
            ])
            finished = not batch['hasMore']
            offset = batch['offset']

        return output

    def _get_path(self, subpath: str):
        return 'crm-objects/v{}/{}'.format(
            self.options.get('version') or PRODUCTS_API_VERSION, subpath
        )
