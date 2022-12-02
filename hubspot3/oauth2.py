"""
hubspot OAuth2 api
"""
from urllib.parse import urlencode
from hubspot3.base import BaseClient
from hubspot3.utils import get_log
from typing import Optional


OAUTH2_API_VERSION = "1"


class OAuth2Client(BaseClient):
    """
    The hubspot3 OAuth2 client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        """initialize a contacts client"""
        # Since this client is used to generate tokens for authentication, it does not require
        # authentication itself.
        kwargs["disable_auth"] = True
        super(OAuth2Client, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.oauth2")
        self.options["content_type"] = "application/x-www-form-urlencoded"
        # Make sure that certain credentials that wouldn't be used anyway are not set. Not having
        # an access token will also make sure that the `_call_raw` implementation does not try to
        # refresh access tokens on its own.
        self.api_key = None
        self.access_token = None

    def _get_path(self, subpath: str) -> str:
        return f"oauth/v{OAUTH2_API_VERSION}/{subpath}"

    def get_tokens(
        self,
        authorization_code: str,
        redirect_uri: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        **options,
    ):
        """
        Request an initial token pair using the provided credentials.

        If any of the optional parameters are not provided, their value will be read from the
        corresponding attributes on this client.
        If the value for all optional parameters had to be read from the attributes, the refresh
        token returned from the API will be stored on this client to allow for further
        `refresh_token` calls without having to provide the refresh token.

        :see: https://developers.hubspot.com/docs/methods/oauth2/get-access-and-refresh-tokens
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id or self.client_id,
            "client_secret": client_secret or self.client_secret,
            "redirect_uri": redirect_uri,
            "code": authorization_code,
        }
        result = self._call("token", method="POST", data=urlencode(data), **options)

        if not client_id and not client_secret:
            self.refresh_token = result["refresh_token"]
        return result

    def refresh_tokens(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        **options,
    ):
        """
        Request a new token pair using the provided refresh token and credentials.

        If any of the optional parameters are not provided, their value will be read from the
        corresponding attributes on this client.
        If the value for all optional parameters had to be read from the attributes, the refresh
        token returned from the API will be stored on this client to allow for further
        `refresh_token` calls without having to provide the refresh token.

        :see: https://developers.hubspot.com/docs/methods/oauth2/refresh-access-token
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": client_id or self.client_id,
            "client_secret": client_secret or self.client_secret,
            "refresh_token": refresh_token or self.refresh_token,
        }
        result = self._call("token", method="POST", data=urlencode(data), **options)

        if not client_id and not client_secret and not refresh_token:
            self.refresh_token = result["refresh_token"]
        return result

    def get_access_token_data(self, access_token: str, **options):
        """
        Get the meta data for an access token.

        :see: https://developers.hubspot.com/docs/methods/oauth2/get-access-token-information
        """
        return self._call(f"access-tokens/{access_token}", **options)

    def get_refresh_token_data(self, refresh_token: Optional[str] = None, **options):
        """
        Get the meta data for a refresh token.

        If any of the optional parameters are not provided, their value will be read from the
        corresponding attributes on this client.

        :see: https://developers.hubspot.com/docs/methods/oauth2/get-refresh-token-information
        """
        return self._call(
            f"refresh-tokens/{refresh_token or self.refresh_token}", **options
        )

    def delete_refresh_token(self, refresh_token: Optional[str] = None):
        """
        Deletes a refresh token. You can use this to delete your refresh token if a user
        uninstalls your app.

        If any of the optional parameters are not provided, their value will be read from the
        corresponding attributes on this client.

        :see: https://developers.hubspot.com/docs/methods/oauth2/delete-refresh-token
        """
        return self._call(
            f"refresh-tokens/{refresh_token or self.refresh_token}",
            method="DELETE",
        )
