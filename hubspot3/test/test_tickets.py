"""
testing hubspot3.tickets
"""
import json
from unittest.mock import Mock

import pytest

from hubspot3.tickets import TicketsClient
from hubspot3.test.globals import TEST_KEY

TICKETS = TicketsClient(api_key=TEST_KEY)
# since we need to have an id to submit and to attempt to get a ticket,
# we need to be hacky here and fetch one upon loading this file.
BASE_TICKET = TICKETS.get_all(limit=1)[0]


@pytest.fixture
def tickets_client(mock_connection):
    client = TicketsClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


def test_create_ticket():
    """
    tests creating a ticket
    :see: https://developers.hubspot.com/docs/methods/tickets/create-ticket
    """
    with pytest.raises(Exception):
        TICKETS.create("", "")

    ticket = TICKETS.create("688840", "688845", properties={"subject": "test_hubspot3"})
    assert ticket
    assert isinstance(ticket, dict)


def test_get_ticket():
    """
    tests getting a ticket by id
    :see: https://developers.hubspot.com/docs/methods/tickets/get_ticket_by_id
    """
    with pytest.raises(Exception):
        TICKETS.get("")

    ticket = TICKETS.get(BASE_TICKET["objectId"])
    assert ticket
    assert isinstance(ticket, dict)


def test_get_all_tickets():
    """
    tests getting all tickets
    :see: https://developers.hubspot.com/docs/methods/tickets/get-all-tickets
    """
    tickets = TICKETS.get_all()
    assert tickets
    assert isinstance(tickets, list)
    assert len(tickets) > 1


@pytest.mark.parametrize(
    "extra_properties_given, extra_properties_as_list",
    [
        (None, []),
        ("lead_source", ["lead_source"]),
        (
            ["hs_analytics_last_url", "hs_analytics_revenue"],
            ["hs_analytics_last_url", "hs_analytics_revenue"],
        ),
    ],
)
def test_get_batch(
    tickets_client,
    mock_connection,
    extra_properties_given,
    extra_properties_as_list,
):
    response_body = {
        "3234574": {"objectId": 3234574, "properties": {}},
        "3234575": {"objectId": 3234575, "properties": {}},
    }
    ids = ["3234574", "3234575"]
    properties = tickets_client.default_batch_properties.copy()
    properties.extend(extra_properties_as_list)
    params = {"properties": p for p in properties}

    mock_connection.set_response(200, json.dumps(response_body))
    resp = tickets_client.get_batch(ids, extra_properties_given)
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request(
        "POST", "/crm-objects/v1/objects/tickets/batch-read", **params, data={'ids': ids}
    )
    assert len(resp) == 2
    assert {"id": 3234574} in resp
    assert {"id": 3234575} in resp


@pytest.mark.parametrize(
    "extra_properties_given, extra_properties_as_list",
    [
        (None, []),
        ("lead_source", ["lead_source"]),
        (
            ["hs_analytics_last_url", "hs_analytics_revenue"],
            ["hs_analytics_last_url", "hs_analytics_revenue"],
        ),
    ],
)
def test_get_batch_with_history(
    tickets_client,
    mock_connection,
    extra_properties_given,
    extra_properties_as_list,
):
    response_body = {
        "3234574": {"objectId": 3234574, "properties": {}},
        "3234575": {"objectId": 3234575, "properties": {}},
    }
    ids = ["3234574", "3234575"]
    properties = tickets_client.default_batch_properties.copy()
    properties.extend(extra_properties_as_list)
    params = {"propertiesWithHistory": p for p in properties}

    mock_connection.set_response(200, json.dumps(response_body))
    resp = tickets_client.get_batch_with_history(ids, extra_properties_given)
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request(
        "POST", "/crm-objects/v1/objects/tickets/batch-read", **params, data={'ids': ids}
    )
    assert len(resp) == 2
    for single_id in ids:
        assert single_id in resp


def base_get_recently(
    tickets_client,
    mock_connection,
    changeType
):
    response_body_recent = [
        {
            'timestamp': 1571409899877,
            'changeType': 'CHANGED',
            'objectId': 47005994,
            'changes':
            {
                'changedProperties': ['hs_lastcontacted', 'hs_last_email_activity'],
                'newAssociations': [],
                'removedAssociations': [],
                'newListMemberships': [],
                'removedListMemberships': [],
            }
        },
        {
            'timestamp': 1571411169000,
            'changeType': 'CREATED',
            'objectId': 47005994,
            'changes':
            {
                'changedProperties': ['hs_lastcontacted', 'hs_last_email_activity'],
                'newAssociations': [],
                'removedAssociations': [],
                'newListMemberships': [],
                'removedListMemberships': [],
            }
        }
    ]
    response_body_batch = {
        '47005994': {
            'objectType': 'TICKET',
            'portalId': 5282301,
            'objectId': 47005994,
            'properties': {
                'hs_lastcontacted': {
                    'versions': [{
                        'name': 'hs_lastcontacted',
                        'value': '1571427728000',
                        'timestamp': 1571411169418,
                        'sourceId': 'TicketsRollupProperties',
                        'source': 'CALCULATED',
                        'sourceVid': []
                    }, {
                        'name': 'hs_lastcontacted',
                        'value': '1571415325000',
                        'timestamp': 1571410899877,
                        'sourceId': 'TicketsRollupProperties',
                        'source': 'CALCULATED',
                        'sourceVid': []
                    }],
                    'value': '1571427728000',
                    'timestamp': 1571411169418,
                    'source': 'CALCULATED',
                    'sourceId': 'TicketsRollupProperties'
                },
                'hs_last_email_activity': {
                    'versions': [{
                        'name': 'hs_last_email_activity',
                        'value': 'SENT_TO_CONTACT',
                        'timestamp': 1571411169118,
                        'sourceId': 'TicketsRollupProperties',
                        'source': 'CALCULATED',
                        'sourceVid': []
                    }, {
                        'name': 'hs_last_email_activity',
                        'value': 'REPLY_FROM_CONTACT',
                        'timestamp': 1571409899877,
                        'sourceId': 'TicketsRollupProperties',
                        'source': 'CALCULATED',
                        'sourceVid': []
                    }],
                    'value': 'SENT_TO_CONTACT',
                    'timestamp': 1571411169118,
                    'source': 'CALCULATED',
                    'sourceId': 'TicketsRollupProperties'
                }
            }
        }
    }
    ids = [47005994]
    properties = ['hs_lastcontacted', 'hs_last_email_activity']
    params_batch = {"propertiesWithHistory": p for p in properties}
    params_recent = {
        'objectId': 47005994,
        'timestamp': 1571411169000,
        'changeType': changeType
    }

    mock_connection.set_responses([(200, json.dumps(response_body_recent)),
                                   (200, json.dumps(response_body_batch)),
                                   (200, '[]')])
    if changeType == 'CHANGED':
        changes = tickets_client.get_recently_modified(time_offset=1571847002)
    else:
        changes = tickets_client.get_recently_created(time_offset=1571847002)
    mock_connection.assert_num_requests(3)

    mock_connection.assert_has_request(
        "GET", "/crm-objects/v1/change-log/ticket", **params_recent
    )
    mock_connection.assert_has_request(
        "POST", "/crm-objects/v1/objects/tickets/batch-read", **params_batch, data={'ids': ids},
    )
    assert len(changes) == 2
    assert [change['objectId'] for change in changes] == [change['objectId'] for
                                                          change in response_body_recent]
    assert len(changes[0]['changes']['changedValues']) == 1
    assert len(changes[1]['changes']['changedValues']) == 2


def test_get_recently_created(
    tickets_client,
    mock_connection,
):
    base_get_recently(tickets_client, mock_connection, 'CREATED')


def test_get_recently_modified(
    tickets_client,
    mock_connection,
):
    base_get_recently(tickets_client, mock_connection, 'CHANGED')
