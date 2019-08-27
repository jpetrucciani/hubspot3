"""
hubspot properties api
"""
from typing import Dict

from hubspot3.base import BaseClient
from hubspot3.globals import (
    OBJECT_TYPE_COMPANIES,
    OBJECT_TYPE_CONTACTS,
    OBJECT_TYPE_DEALS,
    OBJECT_TYPE_LINE_ITEMS,
    OBJECT_TYPE_PRODUCTS,
    VALID_PROPERTY_DATA_TYPES,
    VALID_PROPERTY_WIDGET_TYPES,
    DATA_TYPE_ENUM,
)
from hubspot3.utils import get_log

PROPERTIES_API_VERSION = {
    OBJECT_TYPE_COMPANIES: "1",
    OBJECT_TYPE_CONTACTS: "1",
    OBJECT_TYPE_DEALS: "1",
    OBJECT_TYPE_LINE_ITEMS: "2",
    OBJECT_TYPE_PRODUCTS: "2",
}


class PropertiesClient(BaseClient):
    """
    The hubspot3 Properties client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    # Used to store a current object_type. This will be used in `_get_path` to generate the
    # appropriate path to use.
    _object_type = None

    def __init__(self, *args, **kwargs):
        super(PropertiesClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.properties")

    def _get_path(self, subpath):
        return "properties/v{}/{}/properties/{}".format(
            PROPERTIES_API_VERSION[self._object_type], self._object_type, subpath
        )

    @staticmethod
    def _validate(data_type: str, widget_type: str, extra_params: dict) -> None:
        if data_type:
            if data_type not in VALID_PROPERTY_DATA_TYPES:
                raise ValueError(
                    "Invalid data type for property. Valid data types are: {}".format(
                        VALID_PROPERTY_DATA_TYPES
                    )
                )

            if data_type == DATA_TYPE_ENUM and (
                not extra_params or not extra_params.get("options")
            ):
                raise ValueError(
                    "Invalid data for updating an enumeration type. Its 'options' have to be specified."
                )

        if widget_type and widget_type not in VALID_PROPERTY_WIDGET_TYPES:
            raise ValueError(
                "Invalid widget type for property. Valid widget types are: {}".format(
                    VALID_PROPERTY_WIDGET_TYPES
                )
            )

    def create(
        self,
        object_type: str,
        code: str,
        label: str,
        description: str,
        group_code: str,
        data_type: str,
        widget_type: str,
        extra_params: dict = None,
    ) -> Dict:
        """
        Create a new custom property on hubspot.
        """
        extra_params = extra_params or {}

        self._validate(data_type, widget_type, extra_params)

        # Save the current object type.
        self._object_type = object_type

        return self._call(
            "",
            method="POST",
            data={
                "name": code,
                "label": label,
                "description": description,
                "groupName": group_code,
                "type": data_type,
                "fieldType": widget_type,
                **extra_params,
            },
        )

    def update(
        self,
        object_type: str,
        code: str,
        label: str = None,
        description: str = None,
        group_code: str = None,
        data_type: str = None,
        widget_type: str = None,
        extra_params: dict = None,
    ) -> Dict:
        """
        Update a custom property on hubspot.
        """

        extra_params = extra_params or {}

        self._validate(data_type, widget_type, extra_params)

        # Save the current object type.
        self._object_type = object_type

        fields = {
            "label": label,
            "description": description,
            "groupName": group_code,
            "type": data_type,
            "fieldType": widget_type,
            **extra_params,
        }
        data = {key: value for key, value in fields.items() if value is not None}

        return self._call("named/{}".format(code), method="PUT", data=data)

    def get_all(self, object_type):
        """Retrieve all the custom properties."""

        # Save the current object type.
        self._object_type = object_type

        return self._call(
            "", method="GET", params={"properties": ["name", "label", "description"]}
        )

    def delete(self, object_type, code):
        """Delete a custom property."""

        # Save the current object type.
        self._object_type = object_type

        return self._call("named/{}".format(code), method="DELETE")

    def delete_all(self, object_type):
        """Delete all the custom properties. Please use it carefully."""
        props_data = self.get_all(object_type)

        for prop_data in props_data:
            if not prop_data["hubspotDefined"]:
                self.delete(object_type, prop_data["name"])
