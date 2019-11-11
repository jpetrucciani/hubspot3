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


def test_get_all_tickets(tickets_client, mock_connection):
    """
    tests getting all tickets
    :see: https://developers.hubspot.com/docs/methods/tickets/get-all-tickets
    """
    response_bodies = [{
        "objects": [
            {
                "addedAt": 1390574181854,
                "objectId": 204726,
                "properties": {"prop_1": 1},
            }
        ],
        "hasMore": True,
        "offset": 204727,
    }, {"objects": [], "hasMore": True, "offset": 204727}, {
        "objects": [
            {
                "addedAt": 1390574181854,
                "objectId": 204727,
                "properties": {"prop_1": 1},
            }
        ],
        "hasMore": False,
        "offset": 204727,
    }, {
        "objects": [
            {
                "addedAt": 1390574181854,
                "objectId": 204727,
                "properties": {"prop_2": 1},
            },
            {
                "addedAt": 1390574181854,
                "objectId": 204728,
                "properties": {"prop_2": 1},
            }
        ],
        "hasMore": False,
        "offset": 204727,
    }]

    # This extra properties are enough to generate 2 requests
    extra_properties = [str(num) for num in range(2000)]

    responses = [(200, response_body) for response_body in response_bodies]
    mock_connection.set_responses(responses)

    tickets = tickets_client.get_all(extra_properties=extra_properties)

    mock_connection.assert_num_requests(4)
    for extra_property in extra_properties:
        # This checks if a request had the URL and includes the given parameters
        mock_connection.assert_has_request(
            "GET", "/crm-objects/v1/objects/tickets/paged", **{"properties": extra_property}
        )

    assert len(tickets) == 3

    first_ticket = [ticket for ticket in tickets if ticket["objectId"] == 204726][0]
    second_ticket = [ticket for ticket in tickets if ticket["objectId"] == 204727][0]
    third_ticket = [ticket for ticket in tickets if ticket["objectId"] == 204728][0]

    assert set(first_ticket["properties"].keys()) == {"prop_1"}
    assert set(second_ticket["properties"].keys()) == {"prop_1", "prop_2"}
    assert set(third_ticket["properties"].keys()) == {"prop_2"}


@pytest.mark.parametrize(
    "extra_properties_given, extra_properties_as_list",
    [(None, []),
     ("lead_source", ["lead_source"]),
     (["hs_analytics_last_url", "hs_analytics_revenue"],
      ["hs_analytics_last_url", "hs_analytics_revenue"]
      )
     ]
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
    properties = TicketsClient.default_batch_properties.copy()
    properties.extend(extra_properties_as_list)

    mock_connection.set_response(200, json.dumps(response_body))
    tickets = tickets_client.get_batch(ids, extra_properties_given)
    mock_connection.assert_num_requests(1)
    for one_property in properties:
        # Underling function only accepts one value per parameter
        params = {"properties": one_property}
        mock_connection.assert_has_request(
            "POST", "/crm-objects/v1/objects/tickets/batch-read", **params, data={"ids": ids}
        )
    assert len(tickets) == 2
    response_ids = [ticket["id"] for ticket in tickets]
    for single_id in ids:
        assert int(single_id) in response_ids


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
    properties = TicketsClient.default_batch_properties.copy()
    properties.extend(extra_properties_as_list)

    mock_connection.set_response(200, json.dumps(response_body))
    resp = tickets_client.get_batch_with_history(ids, extra_properties_given)
    mock_connection.assert_num_requests(1)
    for one_property in properties:
        # Underling function only accepts one value per parameter
        params = {"propertiesWithHistory": one_property}
        mock_connection.assert_has_request(
            "POST", "/crm-objects/v1/objects/tickets/batch-read", **params, data={"ids": ids}
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
            "timestamp": 1571409899877,
            "changeType": "CHANGED",
            "objectId": 47005994,
            "changes":
            {
                "changedProperties": ["hs_lastcontacted", "hs_last_email_activity"],
                "newAssociations": [],
                "removedAssociations": [],
                "newListMemberships": [],
                "removedListMemberships": [],
            }
        },
        {
            "timestamp": 1571411169000,
            "changeType": "CREATED",
            "objectId": 47005994,
            "changes":
            {
                "changedProperties": ["hs_lastcontacted", "hs_last_email_activity"],
                "newAssociations": [],
                "removedAssociations": [],
                "newListMemberships": [],
                "removedListMemberships": [],
            }
        }
    ]

    params_recent = {
        "objectId": 47005994,
        "timestamp": 1571411169000,
        "changeType": changeType
    }

    mock_connection.set_responses([(200, json.dumps(response_body_recent)),
                                   (200, "[]")])
    if changeType == "CHANGED":
        get_recently_method = tickets_client.get_recently_modified
    else:
        get_recently_method = tickets_client.get_recently_created
    changes = get_recently_method(time_offset=1571847002)
    mock_connection.assert_num_requests(2)

    mock_connection.assert_has_request(
        "GET", "/crm-objects/v1/change-log/ticket", **params_recent
    )

    assert len(changes) == 2
    assert changes == response_body_recent


def test_get_recently_created(
    tickets_client,
    mock_connection,
):
    base_get_recently(tickets_client, mock_connection, "CREATED")


def test_get_recently_modified(
    tickets_client,
    mock_connection,
):
    base_get_recently(tickets_client, mock_connection, "CHANGED")
