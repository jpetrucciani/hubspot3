"""
testing hubspot3.deals
"""
import pytest
from hubspot3.deals import DealsClient
from hubspot3.error import HubspotNotFound, HubspotBadRequest
from hubspot3.test.globals import TEST_KEY
from hubspot3 import deals
import json
from unittest.mock import Mock

DEALS = DealsClient(api_key=TEST_KEY)


@pytest.fixture
def deals_client(mock_connection):
    client = deals.DealsClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


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


def test_delete_deal():
    """
    Test the deletion of a deal.
    :see: https://developers.hubspot.com/docs/methods/deals/delete_deal
    """
    data = {
        "properties": [
            {"value": "Test deal", "name": "dealname"},
            {"value": None, "name": "createdate"},
        ]
    }
    response_data = DEALS.create(data)
    deal_id = response_data["dealId"]
    DEALS.delete(deal_id)
    with pytest.raises(HubspotNotFound):
        DEALS.get(deal_id)


def test_get_recently_created():
    """
    gets recently created deals
    :see: https://developers.hubspot.com/docs/methods/deals/get_deals_created
    """
    new_deals = DEALS.get_recently_created(limit=20)
    # assert new_deals
    assert len(new_deals) <= 20
    # assert _is_deal(new_deals[0])


def test_get_recently_modified():
    """
    gets recently modified deals
    :see: https://developers.hubspot.com/docs/methods/deals/get_deals_modified
    """
    modified_deals = DEALS.get_recently_created(limit=20)
    # assert modified_deals
    assert len(modified_deals) <= 20
    # assert _is_deal(modified_deals[0])


@pytest.mark.parametrize(
    "start_date, end_date",
    [
        (20, 40)
    ],
)
def test_get_recently_modified_in_interval(
    deals_client,
    mock_connection,
    start_date,
    end_date,
):
    """
    gets recently modified deals
    :see: https://developers.hubspot.com/docs/methods/deals/get_deals_modified
    """
    params = {"since": start_date}
    response_body = {
        "hasMore": False,
        "offset": 2,
        "total": 2477,
        "results": [
            {
                "portalId": 62515,
                "dealId": 38818613,
                "isDeleted": False,
                "associations": {
                    "associatedVids": [1572024],
                    "associatedCompanyIds": [],
                    "associatedDealIds": []
                },
                "properties": {
                    "pipeline": {
                        "value": "default",
                        "timestamp": 1463680280365,
                        "source": None,
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "pipeline",
                                "value": "default",
                                "timestamp": 1463680280365,
                                "sourceVid": []
                            }
                        ]
                    },
                    "dealname": {
                        "value": "SELLERSQ-national",
                        "timestamp": 1463680280348,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "dealname",
                                "value": "SELLERSQ-national",
                                "timestamp": 1463680280348,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "email_address": {
                        "value": "sateesh@sellersq.com",
                        "timestamp": 1463680280348,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "email_address",
                                "value": "sateesh@sellersq.com",
                                "timestamp": 1463680280348,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "hs_lastmodifieddate": {
                        "value": "30",
                        "timestamp": 30,
                        "source": "CALCULATED",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "hs_lastmodifieddate",
                                "value": "1463680280357",
                                "timestamp": 1463680280357,
                                "source": "CALCULATED",
                                "sourceVid": []
                            }
                        ]
                    },
                    "num_associated_contacts": {
                        "value": "1",
                        "timestamp": 0,
                        "source": "CALCULATED",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "num_associated_contacts",
                                "value": "1",
                                "source": "CALCULATED",
                                "sourceVid": []
                            }
                        ]
                    },
                    "dealstage": {
                        "value": "appointmentscheduled",
                        "timestamp": 1463680280348,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "dealstage",
                                "value": "appointmentscheduled",
                                "timestamp": 1463680280348,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "hs_createdate": {
                        "value": "1463680280357",
                        "timestamp": 1463680280357,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "hs_createdate",
                                "value": "1463680280357",
                                "timestamp": 1463680280357,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "createdate": {
                        "value": "1463680280357",
                        "timestamp": 1463680280357,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "createdate",
                                "value": "1463680280357",
                                "timestamp": 1463680280357,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "source": {
                        "value": "Unknown",
                        "timestamp": 1463680280348,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "source",
                                "value": "Unknown",
                                "timestamp": 1463680280348,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "contact_number": {
                        "value": "919000884201",
                        "timestamp": 1463680280348,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "contact_number",
                                "value": "919000884201",
                                "timestamp": 1463680280348,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    }
                },
                "imports": []
            },
            {
                "portalId": 62515,
                "dealId": 25922214,
                "isDeleted": False,
                "associations": {
                    "associatedVids": [1571574],
                    "associatedCompanyIds": [],
                    "associatedDealIds": []
                },
                "properties": {
                    "pipeline": {
                        "value": "default",
                        "timestamp": 1463676642461,
                        "source": None,
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "pipeline",
                                "value": "default",
                                "timestamp": 1463676642461,
                                "sourceVid": []
                            }
                        ]
                    },
                    "dealname": {
                        "value": "sachin16495-national",
                        "timestamp": 1463676642448,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "dealname",
                                "value": "sachin16495-national",
                                "timestamp": 1463676642448,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "email_address": {
                        "value": "spsachinonspot@gmail.com",
                        "timestamp": 1463676642448,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "email_address",
                                "value": "spsachinonspot@gmail.com",
                                "timestamp": 1463676642448,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "hs_lastmodifieddate": {
                        "value": "10",
                        "timestamp": 10,
                        "source": "CALCULATED",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "hs_lastmodifieddate",
                                "value": "1463676642456",
                                "timestamp": 1463676642456,
                                "source": "CALCULATED",
                                "sourceVid": []
                            }
                        ]
                    },
                    "num_associated_contacts": {
                        "value": "1",
                        "timestamp": 0,
                        "source": "CALCULATED",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "num_associated_contacts",
                                "value": "1",
                                "source": "CALCULATED",
                                "sourceVid": []
                            }
                        ]
                    },
                    "dealstage": {
                        "value": "appointmentscheduled",
                        "timestamp": 1463676642448,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "dealstage",
                                "value": "appointmentscheduled",
                                "timestamp": 1463676642448,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "hs_createdate": {
                        "value": "1463676642456",
                        "timestamp": 1463676642456,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "hs_createdate",
                                "value": "1463676642456",
                                "timestamp": 1463676642456,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "createdate": {
                        "value": "1463676642456",
                        "timestamp": 1463676642456,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "createdate",
                                "value": "1463676642456",
                                "timestamp": 1463676642456,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "source": {
                        "value": "Unknown",
                        "timestamp": 1463676642448,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "source",
                                "value": "Unknown",
                                "timestamp": 1463676642448,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    },
                    "contact_number": {
                        "value": "919410249255",
                        "timestamp": 1463676642448,
                        "source": "API",
                        "sourceId": None,
                        "versions": [
                            {
                                "name": "contact_number",
                                "value": "919410249255",
                                "timestamp": 1463676642448,
                                "source": "API",
                                "sourceVid": []
                            }
                        ]
                    }
                },
                "imports": []
            }
        ]
    }
    mock_connection.set_response(200, json.dumps(response_body))
    modified_deals = list(deals_client.get_recently_modified_in_interval(start_date, end_date))
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request(
        "GET", "/deals/v1/deal/recent/modified", **params
    )
    assert len(modified_deals) == 1
