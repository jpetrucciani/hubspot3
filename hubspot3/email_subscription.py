"""
hubspot email subscription api
"""
from typing import Dict, Iterable, Mapping
from hubspot3.base import BaseClient
from hubspot3.utils import get_log


EMAIL_SUBSCRIPTION_API_VERSION = "1"


class EmailSubscriptionClient(BaseClient):
    """
    The hubspot3 Email Subscription client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    class OptState:
        """opt state enum"""

        OPT_IN = "OPT_IN"
        OPT_OUT = "OPT_OUT"
        NOT_OPTED = "NOT_OPTED"

    class LegalBasis:
        """legal basis enum"""

        CONSENT_WITH_NOTICE = "CONSENT_WITH_NOTICE"
        LEGITIMATE_INTEREST_PQL = "LEGITIMATE_INTEREST_PQL"
        LEGITIMATE_INTEREST_CLIENT = "LEGITIMATE_INTEREST_CLIENT"
        NON_GDPR = "NON_GDPR"
        PERFORMANCE_OF_CONTRACT = "PERFORMANCE_OF_CONTRACT"

    def __init__(self, *args, **kwargs):
        """initialize an email subscription client"""
        super(EmailSubscriptionClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.email_subscription")

    def _get_path(self, subpath):
        return "email/public/v{}/subscriptions/{}".format(
            EMAIL_SUBSCRIPTION_API_VERSION, subpath
        )

    def get_status(self, email: str, portal_id: int = None, **options) -> Dict:
        """
        Retrieve the email subscription status for the given email address.
        :see: https://developers.hubspot.com/docs/methods/email/get_status
        """
        params = {}
        if portal_id is not None:
            params["portalId"] = portal_id
        return self._call(email, method="GET", params=params, **options)

    def update_status(self, email: str, data: Mapping, **options) -> None:
        """
        Update the email subscription status for the given email address using the given raw data.
        :see: https://developers.hubspot.com/docs/methods/email/update_status
        """
        self._call(email, method="PUT", data=dict(data), **options)

    def update_subscriptions(
        self,
        email: str,
        subscriptions: Iterable,
        portal_legal_basis: str = None,
        portal_legal_basis_explanation: str = None,
        **options
    ) -> None:
        """
        Convenience method to update the individual email subscriptions for a given email address.
        :see: https://developers.hubspot.com/docs/methods/email/update_status
        """
        data = {"subscriptionStatuses": list(subscriptions)}
        if portal_legal_basis:
            data["portalSubscriptionLegalBasis"] = portal_legal_basis
        if portal_legal_basis_explanation:
            data[
                "portalSubscriptionLegalBasisExplanation"
            ] = portal_legal_basis_explanation
        self.update_status(email, data, **options)

    def unsubscribe_permanently(self, email: str, **options) -> None:
        """
        Convenience method to unsubscribe an email address from all email subscriptions
        permanently, i.e. this email address cannot be added opted into any email subscription
        anymore.
        :see: https://developers.hubspot.com/docs/methods/email/update_status
        """
        self.update_status(email, {"unsubscribeFromAll": True}, **options)

    def get_subscription_types(self, portal_id: int = None, **options) -> Dict:
        """
        Retrieve all newsletter subscription types.
        :see: https://developers.hubspot.com/docs/methods/email/get_subscriptions
        """
        params = {}
        if portal_id is not None:
            params["portalId"] = portal_id
        return self._call("", method="GET", params=params, **options)
