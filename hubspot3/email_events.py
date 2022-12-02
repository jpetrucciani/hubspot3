"""
hubspot email events api
"""
from typing import Optional
from hubspot3.base import BaseClient
from hubspot3.utils import get_log


EMAIL_EVENTS_API_VERSION = "1"


class EmailEventsClient(BaseClient):
    """
    The hubspot3 Email Events client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        """initialize an email events client"""
        super(EmailEventsClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.email_events")

    def _get_path(self, subpath):
        return f"email/public/v{EMAIL_EVENTS_API_VERSION}/campaigns/{subpath}"

    def get_all_campaigns_ids(self, **options):
        """
        Retrieve all email campaign IDs associated with the portal.
        :see: https://developers.hubspot.com/docs/methods/email/get_campaigns_by_id
        """
        return self._call("by-id", **options)

    def get_campaign_data(self, campaign_id: Optional[int] = None, **options):
        """
        Retrieve campaign data for a given campaign ID.
        :see: https://developers.hubspot.com/docs/methods/email/get_campaign_data
        :param campaign_id:
        """
        if campaign_id is not None:
            return self._call(str(campaign_id))
        return None
