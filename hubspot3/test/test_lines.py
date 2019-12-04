"""Tests for the line items client."""

import json
from unittest.mock import Mock, patch

import pytest
from hubspot3 import lines


@pytest.fixture
def lines_client(mock_connection):
    client = lines.LinesClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


class TestLinesClient(object):
    @pytest.mark.parametrize(
        "subpath, expected_value",
        [
            ("", "crm-objects/v1/objects/line_items/"),
            ("batch-create", "crm-objects/v1/objects/line_items/batch-create"),
            ("batch-read", "crm-objects/v1/objects/line_items/batch-read"),
        ],
    )
    def test_get_path(self, lines_client, subpath, expected_value):
        assert lines_client._get_path(subpath) == expected_value

    def test_create(self, lines_client, mock_connection):
        data = {
            "properties": [
                {"name": "quantity", "value": "1"},
                {"name": "price", "value": "10.90"},
                {"name": "name", "value": "Custom name for the line item"},
            ]
        }
        response_body = {"objectType": "LINE_ITEM", "objectId": "123456789"}
        mock_connection.set_response(200, json.dumps(response_body))
        resp = lines_client.create(data)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "POST", "/crm-objects/v1/objects/line_items/?", data
        )
        assert resp == response_body

    def test_delete(self, lines_client, mock_connection):
        line_item_id = "1234"
        response_body = {}
        mock_connection.set_response(204, json.dumps(response_body))
        resp = lines_client.delete(line_item_id)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "DELETE", "/crm-objects/v1/objects/line_items/{}?".format(line_item_id)
        )
        assert resp == response_body

    def test_get(self, lines_client, mock_connection):
        line_item_id = "1234"
        response_body = {"objectType": "LINE_ITEM", "objectId": "1234"}
        mock_connection.set_response(200, json.dumps(response_body))
        resp = lines_client.get(line_item_id)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "GET", "/crm-objects/v1/objects/line_items/{}?".format(line_item_id)
        )
        assert resp == response_body

    def test_update(self, lines_client, mock_connection):
        line_item_id = "1234"
        data = {
            "properties": [{"name": "name", "value": "Custom name for the line item"}]
        }
        response_body = {"objectType": "LINE_ITEM", "objectId": "1234"}
        mock_connection.set_response(200, json.dumps(response_body))
        response = lines_client.update(line_item_id, data)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            method="PUT",
            url="/crm-objects/v1/objects/line_items/{}?".format(line_item_id),
            data=data,
        )
        assert response == response_body

    def test_get_all(self, lines_client, mock_connection):
        response_body = {
            "objects": [
                {
                    "objectType": "PRODUCT",
                    "portalId": 62515,
                    "objectId": 1642736,
                    "properties": {},
                    "version": 2,
                    "isDeleted": False,
                },
                {
                    "objectType": "PRODUCT",
                    "portalId": 62515,
                    "objectId": 1642767,
                    "properties": {},
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
        response = lines_client.get_all()

        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            method="GET",
            url="/crm-objects/v1/objects/line_items/paged?offset=0&properties=name&properties=price&properties=quantity",  # noqa: E501
            data=None,
        )

        assert response == [{"id": 1642736}, {"id": 1642767}, {"id": 1642796}]

    @patch("hubspot3.lines.CRMAssociationsClient")
    def test_link_line_item_to_deal(self, mock_associations_client, lines_client):
        mock_instance = mock_associations_client.return_value
        lines_client.link_line_item_to_deal(1, 1)
        mock_associations_client.assert_called_with(
            access_token=None, api_key=None, refresh_token=None,
            oauth2_token_getter=None, oauth2_token_setter=None,
        )
        mock_instance.link_line_item_to_deal.assert_called_with(1, 1)
