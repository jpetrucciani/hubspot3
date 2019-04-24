"""
hubspot settings api
"""
from hubspot3.base import BaseClient
from hubspot3.error import HubspotError
from typing import Dict


SETTINGS_API_VERSION = "v1"


class SettingsClient(BaseClient):
    """
    hubspot3 Settings client
    Use this to read settings for a given API key, as well as update a setting.
    :see: http://docs.hubapi.com/wiki/Settings_API
    """

    def _get_path(self, subpath: str) -> str:
        """get the full api url for the given subpath on this client"""
        return "settings/{}/{}".format(SETTINGS_API_VERSION, subpath)

    def get_settings(self, **options):
        """Returns the settings we know about for this API key."""
        return self._call("settings", **options)

    def get_setting(self, name: str, **options):
        """Returns the specific requested setting name, if found."""
        params = {"name": name}
        return self._call("settings", params=params, **options)

    def update_setting(self, data: Dict, **options):
        """Updates a specific setting for this API key."""
        params = {}
        if data["name"]:
            params["name"] = data["name"]
        if data["value"]:
            params["value"] = data["value"]

        return self._call(
            "settings", params=params, data=data, method="POST", **options
        )

    def delete_setting(self, name: str, **options):
        """Deletes a specific setting by emptying out its value."""
        params = {}
        if name:
            params["name"] = name
        else:
            raise HubspotError("Setting name required.", "settings")
        return self._call("settings", params=params, method="DELETE", **options)
