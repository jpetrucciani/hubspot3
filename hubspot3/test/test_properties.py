"""
testing hubspot3.properties
"""

import json
from unittest.mock import Mock
from typing import Dict

import pytest

from hubspot3 import properties
from hubspot3.globals import (
    OBJECT_TYPE_CONTACTS,
    OBJECT_TYPE_COMPANIES,
    OBJECT_TYPE_DEALS,
    OBJECT_TYPE_LINE_ITEMS,
    OBJECT_TYPE_PRODUCTS,
    DATA_TYPE_BOOL,
    WIDGET_TYPE_BOOLEAN_CHECKBOX,
    DATA_TYPE_ENUM,
)


@pytest.fixture
def properties_client(mock_connection) -> properties.PropertiesClient:
    client = properties.PropertiesClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


@pytest.fixture
def properties_input_data() -> Dict:
    return dict(
        code="my_field",
        label="My Label",
        description="My Description",
        data_type=DATA_TYPE_BOOL,
        widget_type=WIDGET_TYPE_BOOLEAN_CHECKBOX,
    )


class TestPropertiesClient:
    @pytest.mark.parametrize(
        "object_type, api_version",
        [
            (OBJECT_TYPE_CONTACTS, 1),
            (OBJECT_TYPE_COMPANIES, 1),
            (OBJECT_TYPE_DEALS, 1),
            (OBJECT_TYPE_LINE_ITEMS, 2),
            (OBJECT_TYPE_PRODUCTS, 2),
        ],
    )
    def test_get_path(self, object_type: str, api_version: str) -> None:
        client = properties.PropertiesClient(disable_auth=True)
        client._object_type = object_type
        assert (
            client._get_path("")
            == f"properties/v{api_version}/{object_type}/properties/"
        )

    def test_validate_data_type(self) -> None:
        client = properties.PropertiesClient(disable_auth=True)
        with pytest.raises(ValueError) as value_error:
            client._validate(data_type="xy", widget_type=None, extra_params=None)
        assert "Invalid data type for property" in str(value_error)

    def test_validate_widget_type(self) -> None:
        client = properties.PropertiesClient(disable_auth=True)
        with pytest.raises(ValueError) as value_error:
            client._validate(
                data_type=DATA_TYPE_BOOL, widget_type="yz", extra_params=None
            )
        assert "Invalid widget type for property" in str(value_error)

    def test_validate_enum_type(self) -> None:
        client = properties.PropertiesClient(disable_auth=True)
        with pytest.raises(ValueError) as value_error:
            client._validate(
                data_type=DATA_TYPE_ENUM,
                widget_type=WIDGET_TYPE_BOOLEAN_CHECKBOX,
                extra_params=None,
            )
        assert "Invalid data for updating an enumeration type" in str(value_error)

    @pytest.mark.parametrize("extra_params", [None, {"extra": 1}])
    def test_create(
        self, properties_client, mock_connection, properties_input_data, extra_params
    ):
        input_data = properties_input_data
        input_data.update({"extra_params": extra_params}) if extra_params else None
        input_data.update(dict(group_code="custom"))
        response_body = {
            "name": input_data["code"],
            "label": input_data["label"],
            "description": input_data["description"],
            "groupName": input_data["group_code"],
            "type": "string",
            "fieldType": "text",
            "formField": True,
            "displayOrder": -1,
            "options": [],
        }
        data = dict(
            name=input_data["code"],
            label=input_data["label"],
            description=input_data["description"],
            groupName=input_data["group_code"],
            type=input_data["data_type"],
            fieldType=input_data["widget_type"],
        )
        data.update(extra_params or {})

        mock_connection.set_response(200, json.dumps(response_body))
        resp = properties_client.create(
            **dict(object_type=OBJECT_TYPE_CONTACTS, **input_data)
        )
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "POST", "/properties/v1/contacts/properties/?", data
        )
        assert resp == response_body

    @pytest.mark.parametrize("extra_params", [None, {"displayOrder": 3}])
    def test_update(
        self, properties_client, mock_connection, properties_input_data, extra_params
    ):
        input_data = properties_input_data
        input_data.update({"extra_params": extra_params}) or None
        response_body = {
            "name": input_data["code"],
            "label": input_data["label"],
            "description": input_data["description"],
            "groupName": "custom",
            "type": "string",
            "fieldType": "text",
            "formField": True,
            "displayOrder": 3,
            "options": [],
        }
        data = dict(
            label=input_data["label"],
            description=input_data["description"],
            type=input_data["data_type"],
            fieldType=input_data["widget_type"],
        )
        data.update(extra_params or {})

        mock_connection.set_response(200, json.dumps(response_body))
        resp = properties_client.update(
            **dict(object_type=OBJECT_TYPE_CONTACTS, **input_data)
        )
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "PUT",
            f"/properties/v1/contacts/properties/named/{input_data['code']}?",
            data,
        )
        assert resp == response_body

    def test_get(self, properties_client, mock_connection, properties_input_data):
        input_data = properties_input_data
        response_body = {
            "name": input_data["code"],
            "label": input_data["label"],
            "description": input_data["description"],
            "groupName": "custom",
            "type": "string",
            "fieldType": "text",
            "formField": True,
            "displayOrder": 3,
            "options": [],
        }
        mock_connection.set_response(200, json.dumps(response_body))
        resp = properties_client.get(OBJECT_TYPE_DEALS, input_data["code"])
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "GET",
            f"/properties/v1/deals/properties/named/{input_data['code']}?",
        )
        assert resp == response_body
