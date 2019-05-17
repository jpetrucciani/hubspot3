"""
basic testing on the main Hubspot3 client
"""
import pytest
from hubspot3 import Hubspot3, Hubspot3UsageLimits
from hubspot3.error import HubspotBadConfig, HubspotNoConfig
from hubspot3.base import BaseClient
from hubspot3.blog import BlogClient
from hubspot3.broadcast import BroadcastClient
from hubspot3.companies import CompaniesClient
from hubspot3.contact_lists import ContactListsClient
from hubspot3.contacts import ContactsClient
from hubspot3.crm_associations import CRMAssociationsClient
from hubspot3.crm_pipelines import PipelinesClient
from hubspot3.deals import DealsClient
from hubspot3.engagements import EngagementsClient
from hubspot3.forms import FormSubmissionClient
from hubspot3.keywords import KeywordsClient
from hubspot3.leads import LeadsClient
from hubspot3.owners import OwnersClient
from hubspot3.prospects import ProspectsClient
from hubspot3.settings import SettingsClient
from hubspot3.test.globals import TEST_KEY


def test_create_hubspot3_client():
    """attempts to create a hubspot3 client"""
    with pytest.raises(HubspotNoConfig):
        hubspot = Hubspot3()
    with pytest.raises(HubspotBadConfig):
        hubspot = Hubspot3(api_key=TEST_KEY, access_token=TEST_KEY)

    hubspot = Hubspot3(api_key=TEST_KEY)
    assert hubspot

    assert hubspot.usage_limits
    assert isinstance(hubspot.me, dict)
    assert isinstance(hubspot.usage_limits, Hubspot3UsageLimits)
    assert isinstance(hubspot._base, BaseClient)
    assert isinstance(hubspot.blog, BlogClient)
    assert isinstance(hubspot.broadcast, BroadcastClient)
    assert isinstance(hubspot.companies, CompaniesClient)
    assert isinstance(hubspot.contact_lists, ContactListsClient)
    assert isinstance(hubspot.contacts, ContactsClient)
    assert isinstance(hubspot.crm_associations, CRMAssociationsClient)
    assert isinstance(hubspot.crm_pipelines, PipelinesClient)
    assert isinstance(hubspot.deals, DealsClient)
    assert isinstance(hubspot.engagements, EngagementsClient)
    assert isinstance(hubspot.forms, FormSubmissionClient)
    assert isinstance(hubspot.keywords, KeywordsClient)
    assert isinstance(hubspot.leads, LeadsClient)
    assert isinstance(hubspot.owners, OwnersClient)
    assert isinstance(hubspot.prospects, ProspectsClient)
    assert isinstance(hubspot.settings, SettingsClient)
