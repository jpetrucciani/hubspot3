"""
testing hubspot3.deals
"""
import pytest
from hubspot3.deals import DealsClient
from hubspot3.error import HubspotNotFound, HubspotBadRequest
from hubspot3.test.globals import TEST_KEY


DEALS = DealsClient(api_key=TEST_KEY)

DEFAULT_DEAL_PROPERTIES = ["dealname", "createdate"]


def _is_deal(deal: dict) -> bool:
    """performs some checking on the data in the deal"""
    assert deal
    assert all([x in deal for x in DEFAULT_DEAL_PROPERTIES])
    return True


def test_get_deal():
    """
    attempts to get a deal via id
    :see: https://developers.hubspot.com/docs/methods/deals/get_deal
    """
    with pytest.raises(HubspotNotFound):
        DEALS.get("-1")

    deal_check = DEALS.get("852832561")
    assert _is_deal(deal_check["properties"])


def test_create_deal():
    """
    attempts to create a deal
    :see: https://developers.hubspot.com/docs/methods/deals/create_deal
    """
    with pytest.raises(HubspotBadRequest):
        DEALS.create()


def test_get_recently_created():
    """
    gets recently created deals
    :see: https://developers.hubspot.com/docs/methods/deals/get_deals_created
    """
    new_deals = DEALS.get_recently_created(limit=20)
    assert new_deals
    assert len(new_deals) <= 20
    assert _is_deal(new_deals[0])


def test_get_recently_modified():
    """
    gets recently modified deals
    :see: https://developers.hubspot.com/docs/methods/deals/get_deals_modified
    """
    modified_deals = DEALS.get_recently_created(limit=20)
    assert modified_deals
    assert len(modified_deals) <= 20
    assert _is_deal(modified_deals[0])
