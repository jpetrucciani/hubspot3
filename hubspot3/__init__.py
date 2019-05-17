"""
hubspot3 module
"""
from datetime import datetime, timedelta
from hubspot3.error import HubspotBadConfig, HubspotNoConfig
from typing import Any


class Hubspot3UsageLimits:
    """a nicer wrapper for the usage limit data"""

    class FetchStatus:
        """fetch status enum"""

        NONE = ""
        SUCCESS = "SUCCESS"
        CACHED = "CACHED"

    def __init__(
        self,
        collected_at: datetime = datetime.fromtimestamp(0),
        current_usage: int = 0,
        fetch_status: str = FetchStatus.NONE,
        resets_at: datetime = datetime.fromtimestamp(0),
        usage_limit: int = 0,
    ) -> None:
        """usage limits constructor"""
        self.collected_at = collected_at
        self.current_usage = current_usage
        self.fetch_status = fetch_status
        self.resets_at = resets_at
        self.usage_limit = usage_limit

    def __str__(self) -> str:
        """string representation"""
        return "<Hubspot3UsageLimits: {}/{} ({}%) [reset in {}s, cached for {}s]>".format(
            self.current_usage,
            self.usage_limit,
            self.calls_used,
            self.until_reset,
            self.until_cache_expire,
        )

    def __repr__(self) -> str:
        """repr, just use __str__"""
        return self.__str__()

    @property
    def until_reset(self) -> int:
        """returns the number of seconds until limit reset"""
        return int((self.resets_at - datetime.now()).total_seconds())

    @property
    def until_cache_expire(self):
        """returns the number of seconds until the cache expires, and we need an update"""
        return int(
            (self.collected_at + timedelta(minutes=5) - datetime.now()).total_seconds()
        )

    @property
    def calls_remaining(self) -> int:
        """returns the number of calls remaining in your usage limits for the day"""
        return self.usage_limit - self.current_usage

    @property
    def calls_used(self) -> float:
        """returns the percentage of all calls used"""
        return self.current_usage / self.usage_limit

    @property
    def need_update(self):
        """
        true if the data is 'old'.
        data returned by the daily limit endpoint is cached on their end for 5 minutes.
        :see: https://developers.hubspot.com/docs/methods/check-daily-api-usage
        """
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        if self.collected_at and self.collected_at > five_minutes_ago:
            return False
        return True


class Hubspot3:
    """hubspot3 full client class"""

    def __init__(
        self,
        api_key: str = None,
        access_token: str = None,
        refresh_token: str = None,
        client_id: str = None,
        timeout: int = 10,
        api_base: str = "api.hubapi.com",
        debug: bool = False,
        **extra_options: Any
    ) -> None:
        """full client constructor"""
        self.api_key = api_key or extra_options.get("api_key")
        self.access_token = access_token or extra_options.get("access_token")
        self.refresh_token = refresh_token or extra_options.get("refresh_token")
        self.client_id = client_id or extra_options.get("client_id")
        if self.api_key and self.access_token:
            raise HubspotBadConfig("Cannot use both api_key and access_token.")
        if not (self.api_key or self.access_token or self.refresh_token):
            raise HubspotNoConfig("Missing required credentials.")
        self.auth = {
            "access_token": self.access_token,
            "api_key": self.api_key,
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
        }
        self.options = {"api_base": api_base, "debug": debug, "timeout": timeout}
        self.options.update(extra_options)

        # rate limiting related stuff
        self._usage_limits = Hubspot3UsageLimits()

    @property
    def _base(self):
        """returns a hubspot3 base client"""
        from hubspot3.base import BaseClient

        return BaseClient(**self.auth, **self.options)

    @property
    def blog(self):
        """returns a hubspot3 blog client"""
        from hubspot3.blog import BlogClient

        return BlogClient(**self.auth, **self.options)

    @property
    def broadcast(self):
        """returns a hubspot3 broadcast client"""
        from hubspot3.broadcast import BroadcastClient

        return BroadcastClient(**self.auth, **self.options)

    @property
    def companies(self):
        """returns a hubspot3 companies client"""
        from hubspot3.companies import CompaniesClient

        return CompaniesClient(**self.auth, **self.options)

    @property
    def contact_lists(self):
        """returns a hubspot3 contact_lists client"""
        from hubspot3.contact_lists import ContactListsClient

        return ContactListsClient(**self.auth, **self.options)

    @property
    def contacts(self):
        """returns a hubspot3 contacts client"""
        from hubspot3.contacts import ContactsClient

        return ContactsClient(**self.auth, **self.options)

    @property
    def crm_associations(self):
        """returns a hubspot3 crm_associations client"""
        from hubspot3.crm_associations import CRMAssociationsClient

        return CRMAssociationsClient(**self.auth, **self.options)

    @property
    def crm_pipelines(self):
        """returns a hubspot3 crm_pipelines client"""
        from hubspot3.crm_pipelines import PipelinesClient

        return PipelinesClient(**self.auth, **self.options)

    @property
    def deals(self):
        """returns a hubspot3 deals client"""
        from hubspot3.deals import DealsClient

        return DealsClient(**self.auth, **self.options)

    @property
    def engagements(self):
        """returns a hubspot3 engagements client"""
        from hubspot3.engagements import EngagementsClient

        return EngagementsClient(**self.auth, **self.options)

    @property
    def forms(self):
        """returns a hubspot3 forms client"""
        from hubspot3.forms import FormSubmissionClient

        return FormSubmissionClient(**self.auth, **self.options)

    @property
    def keywords(self):
        """returns a hubspot3 keywords client"""
        from hubspot3.keywords import KeywordsClient

        return KeywordsClient(**self.auth, **self.options)

    @property
    def leads(self):
        """returns a hubspot3 leads client"""
        from hubspot3.leads import LeadsClient

        return LeadsClient(**self.auth, **self.options)

    @property
    def owners(self):
        """returns a hubspot3 owners client"""
        from hubspot3.owners import OwnersClient

        return OwnersClient(**self.auth, **self.options)

    @property
    def prospects(self):
        """returns a hubspot3 prospects client"""
        from hubspot3.prospects import ProspectsClient

        return ProspectsClient(**self.auth, **self.options)

    @property
    def settings(self):
        """returns a hubspot3 settings client"""
        from hubspot3.settings import SettingsClient

        return SettingsClient(**self.auth, **self.options)

    @property
    def usage_limits(self):
        """fetches and returns a nice usage liimitation object"""
        if self._usage_limits.need_update:
            limits = self._base._call("integrations/v1/limit/daily")[0]
            self._usage_limits = Hubspot3UsageLimits(
                collected_at=datetime.fromtimestamp(int(limits["collectedAt"]) / 1000),
                current_usage=int(limits["currentUsage"]),
                fetch_status=limits["fetchStatus"],
                resets_at=datetime.fromtimestamp(int(limits["resetsAt"]) / 1000),
                usage_limit=limits["usageLimit"],
            )
        return self._usage_limits

    @property
    def me(self):
        """
        returns info about your hubspot account
        :see: https://developers.hubspot.com/docs/methods/get-account-details
        """
        return self._base._call("integrations/v1/me")
