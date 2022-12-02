"""
testing hubspot3.products
"""
import json
from unittest.mock import Mock

import pytest

from hubspot3 import products


@pytest.fixture
def products_client(mock_connection) -> products.ProductsClient:
    client = products.ProductsClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


# The product id used in our tests.
HUBSPOT_PRODUCT_ID = 1642767


class TestProductsClient:
    """Performs few tests on the Hubspot ProductsClient."""

    def test_get_path(self) -> None:
        client = products.ProductsClient(disable_auth=True)
        assert (
            client._get_path("objects/products/42")
            == "crm-objects/v1/objects/products/42"
        )
        assert (
            client._get_path("objects/products/paged")
            == "crm-objects/v1/objects/products/paged"
        )

    def test_get_product(self, products_client, mock_connection) -> None:
        """Test to retrieve a product from Hubspot by using the ProductsClient."""
        response_body = {"objectType": "PRODUCT", "objectId": HUBSPOT_PRODUCT_ID}

        mock_connection.set_response(200, json.dumps(response_body))
        response = products_client.get_product(str(HUBSPOT_PRODUCT_ID))

        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            method="GET",
            # Notes: name and description properties as the one returned by default.
            url="/crm-objects/v1/objects/products/1642767?properties=name&properties=description",
            data=None,
        )
        assert response == response_body

    def test_get_product_with_extra_properties(
        self, products_client, mock_connection
    ) -> None:
        """
        Test to retrieve a product from Hubspot by using the ProductsClient.

        By default, only `name` and `description`
        properties will be returned if no `properties` is given to the method.
        In this test, we will ask for both 'price' and 'duration' extra properties.
        """
        response_body = {"objectType": "PRODUCT", "objectId": HUBSPOT_PRODUCT_ID}

        mock_connection.set_response(200, json.dumps(response_body))
        response = products_client.get_product(
            str(HUBSPOT_PRODUCT_ID), ["price", "duration"]
        )

        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            method="GET",
            url="/crm-objects/v1/objects/products/1642767?properties=name&properties=description&properties=price&properties=duration",  # noqa: E501
            data=None,
        )
        assert response == response_body

    def test_get_all_products(self, products_client, mock_connection) -> None:
        """Test to retrieve all the products from Hubspot with the default properties."""
        response_body = {
            "objects": [
                {
                    "objectType": "PRODUCT",
                    "portalId": 62515,
                    "objectId": 1642736,
                    "properties": {
                        "name": {
                            "value": "An updated product",
                            "timestamp": 1525287810508,
                            "source": "API",
                            "sourceId": None,
                        },
                        "description": {
                            "value": "This product has a name.",
                            "timestamp": 1525287810508,
                            "source": "API",
                            "sourceId": None,
                        },
                    },
                    "version": 2,
                    "isDeleted": False,
                },
                {
                    "objectType": "PRODUCT",
                    "portalId": 62515,
                    "objectId": 1642767,
                    "properties": {
                        "description": {
                            "value": "This product don't have a name.",
                            "timestamp": 1525287810508,
                            "source": "API",
                            "sourceId": None,
                        }
                    },
                    "version": 1,
                    "isDeleted": False,
                },
                {
                    "objectType": "PRODUCT",
                    "portalId": 62515,
                    "objectId": 1642796,
                    "properties": {},
                    "version": 2,
                    "isDeleted": False,
                },
            ],
            "hasMore": False,
            "offset": 1642796,
        }

        mock_connection.set_response(200, json.dumps(response_body))
        response = products_client.get_all_products()

        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            method="GET",
            url=(
                "/crm-objects/v1/objects/products/paged"
                "?limit=100&offset=0&properties=name&properties=description"
            ),
            data=None,
        )
        assert response == [
            {
                "id": 1642736,
                "name": "An updated product",
                "description": "This product has a name.",
            },
            {"id": 1642767, "description": "This product don't have a name."},
            {"id": 1642796},
        ]

    def test_create_product(self, products_client, mock_connection) -> None:
        """Test to create a new product on Hubspot."""
        product_name = "A new product"
        product_description = "A product to be created"

        response_body = {
            "objectType": "PRODUCT",
            "objectId": HUBSPOT_PRODUCT_ID,
            "properties": {
                "name": {
                    "value": product_name,
                    "timestamp": 1525287096980,
                    "source": "API",
                    "sourceId": None,
                }
            },
            "description": {
                "value": product_description,
                "timestamp": 1525287096980,
                "source": "API",
                "sourceId": None,
            },
        }

        mock_connection.set_response(200, json.dumps(response_body))
        response = products_client.create(
            data=[
                {"name": "name", "value": product_name},
                {"name": "description", "value": product_description},
            ]
        )

        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            method="POST",
            url="/crm-objects/v1/objects/products?",
            data=[
                {"name": "name", "value": product_name},
                {"name": "description", "value": product_description},
            ],
        )
        assert response == response_body

    def test_update_product(self, products_client, mock_connection) -> None:
        """Test to update an existing product on Hubspot."""
        product_name = "An updated product"
        product_description = "A product to be updated"

        response_body = {
            "objectType": "PRODUCT",
            "objectId": HUBSPOT_PRODUCT_ID,
            "properties": {
                "name": {
                    "value": product_name,
                    "timestamp": 1525287096980,
                    "source": "API",
                    "sourceId": None,
                }
            },
            "description": {
                "value": product_description,
                "timestamp": 1525287096980,
                "source": "API",
                "sourceId": None,
            },
        }

        mock_connection.set_response(200, json.dumps(response_body))
        response = products_client.update(
            str(HUBSPOT_PRODUCT_ID),
            data=[
                {"name": "name", "value": product_name},
                {"name": "description", "value": product_description},
            ],
        )

        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            method="PUT",
            url=f"/crm-objects/v1/objects/products/{HUBSPOT_PRODUCT_ID}?",
            data=[
                {"name": "name", "value": product_name},
                {"name": "description", "value": product_description},
            ],
        )
        assert response == response_body
