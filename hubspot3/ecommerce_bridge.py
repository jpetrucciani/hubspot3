"""
hubspot ecommerce bridge api
"""
from collections.abc import Sequence
from typing import List
from hubspot3 import logging_helper
from hubspot3.base import BaseClient


ECOMMERCE_BRIDGE_API_VERSION = "2"
MAX_ECOMMERCE_BRIDGE_SYNC_MESSAGES = 200  # Maximum number of sync messages per request.
MAX_ECOMMERCE_BRIDGE_SYNC_ERRORS = 200  # Maximum number of errors per response.


class EcommerceBridgeClient(BaseClient):
    """
    The hubspot3 Ecommerce Bridge client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    class ObjectType:
        """object type enum"""

        CONTACT = "CONTACT"
        DEAL = "DEAL"
        PRODUCT = "PRODUCT"
        LINE_ITEM = "LINE_ITEM"

    class Action:
        """action enum"""

        DELETE = "DELETE"
        UPSERT = "UPSERT"

    class ErrorType:
        """error type enum"""

        INACTIVE_PORTAL = "INACTIVE_PORTAL"
        NO_SYNC_SETTINGS = "NO_SYNC_SETTINGS"
        SETTINGS_NOT_ENABLED = "SETTINGS_NOT_ENABLED"
        NO_MAPPINGS_DEFINED = "NO_MAPPINGS_DEFINED"
        MISSING_REQUIRED_PROPERTY = "MISSING_REQUIRED_PROPERTY"
        NO_PROPERTIES_DEFINED = "NO_PROPERTIES_DEFINED"
        INVALID_ASSOCIATION_PROPERTY = "INVALID_ASSOCIATION_PROPERTY"
        INVALID_DEAL_STAGE = "INVALID_DEAL_STAGE"
        INVALID_EMAIL_ADDRESS = "INVALID_EMAIL_ADDRESS"
        INVALID_ENUM_PROPERTY = "INVALID_ENUM_PROPERTY"
        UNKNOWN_ERROR = "UNKNOWN_ERROR"

    def __init__(self, *args, **kwargs):
        """initialize an ecommerce bridge client"""
        super(EcommerceBridgeClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.ecommerce_bridge")

    def _get_path(self, subpath):
        return "extensions/ecomm/v{}/{}".format(ECOMMERCE_BRIDGE_API_VERSION, subpath)

    def send_sync_messages(
        self, object_type: str, messages: Sequence, store_id: str = "default", **options
    ) -> None:
        """
        Send multiple ecommerce sync messages for the given object type and store ID.
        If the number of sync messages exceeds the maximum number of sync messages per request,
        the messages will automatically be split up into appropriately sized requests.
        See: https://developers.hubspot.com/docs/methods/ecommerce/v2/send-sync-messages
        """
        # Break the messages down into chunks that do not contain more than the maximum number
        # of allowed sync messages per request.
        chunks = [
            list(messages[i : i + MAX_ECOMMERCE_BRIDGE_SYNC_MESSAGES])
            for i in range(0, len(messages), MAX_ECOMMERCE_BRIDGE_SYNC_MESSAGES)
        ]
        for chunk in chunks:
            data = {"objectType": object_type, "storeId": store_id, "messages": chunk}
            self._call("sync/messages", data=data, method="PUT", **options)

    def _get_sync_errors(
        self,
        subpath: str,
        include_resolved: bool = False,
        error_type: str = None,
        object_type: str = None,
        limit: int = None,
        **options
    ) -> List:
        """Internal method to retrieve sync errors from an endpoint."""
        # Build the common parameters for all requests.
        query_limit = min(
            limit or MAX_ECOMMERCE_BRIDGE_SYNC_ERRORS, MAX_ECOMMERCE_BRIDGE_SYNC_ERRORS
        )
        common_params = {
            "includeResolved": str(include_resolved).lower(),
            "limit": query_limit,
        }
        if error_type:
            common_params["errorType"] = error_type
        if object_type:
            common_params["objectType"] = object_type

        # Potentially perform multiple requests until the given limit is reached or until all
        # errors have been retrieved.
        errors = []
        finished = False
        page = 1
        while not finished:
            batch = self._call(
                subpath, method="GET", params=dict(common_params, page=page), **options
            )
            errors.extend(batch["results"])
            # The "paging" attribute is only present if there are more pages.
            finished = "paging" not in batch or (
                limit is not None and len(errors) >= limit
            )
            # The endpoints use some weird kind of pagination where the page parameter is
            # essentially an offset: page 1 starts with record 1, page 2 with record 2, etc.
            # regardless of the limit parameter. Therefore, the next page must be determined by
            # adding the query limit (instead of 1) to get the next set of errors that weren't
            # already part of the current batch.
            page += query_limit

        return errors[:limit]

    def get_sync_errors_for_account(
        self,
        include_resolved: bool = False,
        error_type: str = None,
        object_type: str = None,
        limit: int = None,
        **options
    ) -> List:
        """
        Retrieve a list of error dictionaries for the account that is associated with the
        credentials used for the connection, optionally filtered/limited, and ordered by recency.
        :see: https://developers.hubspot.com/docs/methods/ecommerce/v2/get-all-sync-errors-for-a-specific-account # noqa
        """
        return self._get_sync_errors(
            "sync/errors/portal",
            include_resolved=include_resolved,
            error_type=error_type,
            object_type=object_type,
            limit=limit,
            **options
        )

    def get_sync_errors_for_app(
        self,
        app_id: int,
        include_resolved: bool = False,
        error_type: str = None,
        object_type: str = None,
        limit: int = None,
        **options
    ) -> List:
        """
        Retrieve a list of error dictionaries for the app with the given ID, optionally
        filtered/limited, and ordered by recency.
        :see: https://developers.hubspot.com/docs/methods/ecommerce/v2/get-all-sync-errors-for-an-app # noqa
        """
        return self._get_sync_errors(
            "sync/errors/app/{app_id}".format(app_id=app_id),
            include_resolved=include_resolved,
            error_type=error_type,
            object_type=object_type,
            limit=limit,
            **options
        )
