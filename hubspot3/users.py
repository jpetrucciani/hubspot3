"""
hubspot users api
"""
from typing import Union

from hubspot3.base import BaseClient

USERS_API_VERSION = "v3"


class UsersClient(BaseClient):
    """
    hubspot3 Users client
    :see: https://developers.hubspot.com/docs/api/settings/user-provisioning
    """

    def _get_path(self, subpath: str):
        """Get the full api url for the given subpath on this client."""
        return "settings/{}/users/{}".format(USERS_API_VERSION, subpath)

    def create(
        self, email: str, role_id: Union[int, str], send_welcome_email: bool = False, **options
    ):
        """Create a new user with minimal contacts-base permissions."""
        data = {
            "email": email,
            "roleId": str(role_id),
            "sendWelcomeEmail": send_welcome_email,
        }
        return self._call(
            "",
            data=data,
            method="POST",
            **options,
        )

    def get_by_id(self, user_id: Union[int, str], **options):
        """Get user specified by ID."""
        return self._call(str(user_id), method="GET", **options)

    def get_roles(self, **options):
        """Get all existing user roles."""
        return self._call("roles", method="GET", **options)
