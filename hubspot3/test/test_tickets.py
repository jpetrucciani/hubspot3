"""
testing hubspot3.tickets
"""
import pytest
from hubspot3.tickets import TicketsClient
from hubspot3.test.globals import TEST_KEY


TICKETS = TicketsClient(api_key=TEST_KEY)


# since we need to have an id to submit and to attempt to get a ticket,
# we need to be hacky here and fetch one upon loading this file.
BASE_TICKET = TICKETS.get_all(limit=1)[0]


def test_create_ticket() -> None:
    """
    tests creating a ticket
    :see: https://developers.hubspot.com/docs/methods/tickets/create-ticket
    """
    with pytest.raises(Exception):
        TICKETS.create("", "")

    ticket = TICKETS.create("688840", "688845", properties={"subject": "test_hubspot3"})
    assert ticket
    assert isinstance(ticket, dict)


def test_get_ticket() -> None:
    """
    tests getting a ticket by id
    :see: https://developers.hubspot.com/docs/methods/tickets/get_ticket_by_id
    """
    with pytest.raises(Exception):
        TICKETS.get("")

    ticket = TICKETS.get(BASE_TICKET["objectId"])
    assert ticket
    assert isinstance(ticket, dict)


def test_get_all_tickets() -> None:
    """
    tests getting all tickets
    :see: https://developers.hubspot.com/docs/methods/tickets/get-all-tickets
    """
    tickets = TICKETS.get_all()
    assert tickets
    assert isinstance(tickets, list)
    assert len(tickets) > 1


def test_update_ticket() -> None:
    """
    tests getting all tickets
    :see: https://developers.hubspot.com/docs/methods/tickets/update-ticket
    """
    ticket = TICKETS.create("688840", "688845", properties={"subject": "test_hubspot3"})
    ticket_update = TICKETS.update(
        ticket["objectId"], data={"subject": "test_hubspot3_update"}
    )
    assert ticket_update
    assert isinstance(ticket_update, dict)
    assert ticket_update["properties"]["subject"]["value"] == "test_hubspot3_update"
