"""
hubspot webhooks api
"""
from enum import Enum
from typing import Dict, List, Optional

from hubspot3.base import BaseClient
from hubspot3.error import HubspotBadConfig

WEBHOOKS_API_VERSION = "v3"


class WebhookEventType(Enum):
    CREATE = "create"
    DELETE = "delete"
    DELETED_FOR_PRIVACY = "deletedForPrivacy"
    NEW_MESSAGE = "newMessage"
    PROPERTY_CHANGE = "propertyChange"


class WebhookObjectType(Enum):
    COMPANY = "company"
    CONTACT = "contact"
    CONVERSATION = "conversation"
    DEAL = "deal"
    LINE_ITEM = "line_item"
    PRODUCT = "product"
    TICKET = "ticket"


class WebhookTimePeriod(Enum):
    SECONDLY = "SECONDLY"
    ROLLING_MINUTE = "ROLLING_MINUTE"


class WebhooksClient(BaseClient):
    """
    hubspot3 Webhooks client

    Note that this client requires the use of a developer account API key and for an app ID to be
    provided when initializing the `Hubspot3()` constructor. This API key cannot be used for common
    CRM functionality like accessing deals and contacts, so be careful about which keys you're using
    for which actions.

    :see: https://developers.hubspot.com/docs/api/webhooks
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We raise these config errors here instead of the `Hubspot3` constructor because the app ID
        # isn't required for the rest of the API.
        if not self.options["disable_auth"]:
            if not self.options["app_id"]:
                raise HubspotBadConfig(
                    "You must provide `app_id` in your configuration to use the webhooks client."
                )
            if not self.api_key:
                raise HubspotBadConfig(
                    "You must use API key authentication to use the webhooks client."
                )

    def _get_path(self, subpath: str):
        """Get the full api url for the given subpath on this client."""
        app_id = self.options["app_id"]
        return f"webhooks/{WEBHOOKS_API_VERSION}/{app_id}/{subpath}"

    def delete_settings(self, **options):
        return self._call("settings", method="DELETE")

    def get_settings(self, **options):
        return self._call("settings", **options)

    def update_settings(
        self,
        target_url: str,
        max_concurrent_requests: int,
        period: WebhookTimePeriod,
        **options,
    ):
        data = {
            "targetUrl": target_url,
            "throttling": {
                "maxConcurrentRequests": max_concurrent_requests,
                "period": period,
            },
        }
        return self._call("settings", data=data, method="PUT", **options)

    def batch_update_subscriptions(
        self, active_by_subscription_id: Dict[int | str, bool], **options
    ):
        data = {
            "inputs": [
                {"id": subscription_id, "active": active}
                for subscription_id, active in active_by_subscription_id.items()
            ]
        }
        return self._call(
            "subscriptions/batch/update", data=data, method="POST", **options
        )

    def create_subscription(
        self,
        object_type: WebhookObjectType,
        event_type: WebhookEventType,
        property_name: Optional[str] = None,
        active: bool = False,
        **options,
    ):
        data = {
            "eventType": f"{object_type}.{event_type}",
            "active": active,
        }
        if property_name:
            data["propertyName"] = property_name
        return self._call("subscriptions", data=data, method="POST", **options)

    def delete_all_subscriptions(self, **options):
        for subscription in self.get_all_subscriptions():
            self.delete_subscription_by_id(subscription["id"])

    def delete_subscription_by_id(self, subscription_id: int | str, **options):
        return self._call(
            f"subscriptions/{subscription_id}", method="DELETE", **options
        )

    def get_all_subscriptions(self, **options) -> List[dict]:
        return self._call("subscriptions", **options)["results"]

    def get_subscription_by_id(self, subscription_id: int | str, **options) -> dict:
        return self._call(f"subscriptions/{subscription_id}", **options)

    def update_subscription_by_id(
        self, subscription_id: int | str, active: bool, **options
    ) -> dict:
        data = {"active": active}
        return self._call(
            f"subscriptions/{subscription_id}", data=data, method="PATCH", **options
        )
