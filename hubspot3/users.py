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
        return f"settings/{USERS_API_VERSION}/users/{subpath}"

    def create(
        self,
        email: str,
        role_id: Union[int, str],
        send_welcome_email: bool = False,
        **options,
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

    def delete_by_email(self, email: str, **options):
        """Delete the user with the specified email address."""
        params = {"idProperty": "EMAIL"}
        return self._call(email, params=params, method="DELETE", **options)

    def delete_by_id(self, user_id: Union[int, str], **options):
        """Delete the user with the specified user ID."""
        return self._call(str(user_id), method="DELETE", **options)

    def get_by_email(self, email: str, **options):
        """Get user with the specified email address."""
        params = {"idProperty": "EMAIL"}
        return self._call(email, params=params, method="GET", **options)

    def get_by_id(self, user_id: Union[int, str], **options):
        """Get user with the specified user ID."""
        return self._call(str(user_id), method="GET", **options)

    def get_roles(self, **options):
        """Get all existing user roles."""
        return self._call("roles", method="GET", **options)

    def update_by_email(self, email: str, role_id: Union[int, str], **options):
        """Update the user with the specified email address."""
        data = {"roleId": str(role_id)}
        params = {"idProperty": "EMAIL"}
        return self._call(email, data=data, method="PUT", params=params, **options)

    def update_by_id(
        self, user_id: Union[int, str], role_id: Union[int, str], **options
    ):
        """Update the user with the specified user ID."""
        data = {"roleId": str(role_id)}
        return self._call(str(user_id), data=data, method="PUT", **options)
