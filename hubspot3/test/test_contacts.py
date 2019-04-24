"""
testing hubspot3.contacts
"""
import pytest
from hubspot3.contacts import ContactsClient
from hubspot3.error import HubspotConflict, HubspotNotFound, HubspotBadRequest
from hubspot3.test.globals import TEST_KEY


CONTACTS = ContactsClient(TEST_KEY)


def test_create_contact():
    """
    attempts to create a contact via the demo api
    :see: https://developers.hubspot.com/docs/methods/contacts/create_contact
    """
    with pytest.raises(HubspotBadRequest):
        CONTACTS.create(data={})

    with pytest.raises(HubspotConflict):
        CONTACTS.create(
            data={
                "properties": [
                    {"property": "email", "value": "testingapis@hubspot.com"},
                    {"property": "firstname", "value": "Adrian"},
                    {"property": "lastname", "value": "Mott"},
                    {"property": "website", "value": "http://hubspot.com"},
                    {"property": "company", "value": "HubSpot"},
                    {"property": "phone", "value": "555-122-2323"},
                    {"property": "address", "value": "25 First Street"},
                    {"property": "city", "value": "Cambridge"},
                    {"property": "state", "value": "MA"},
                    {"property": "zip", "value": "02139"},
                ]
            }
        )


def _is_contact(contact: dict) -> bool:
    """tests some stuff on the contact return object"""
    assert contact
    assert contact["is-contact"]
    assert contact["properties"]
    assert contact["properties"]["firstname"]
    assert contact["properties"]["lastname"]
    assert contact["properties"]["email"]
    return True


def test_get_contact_by_email():
    """
    attempts to fetch a contact via email
    :see: https://developers.hubspot.com/docs/methods/contacts/get_contact_by_email
    """
    with pytest.raises(HubspotNotFound):
        contact = CONTACTS.get_contact_by_email("thisemaildoesnotexist@test.com")

    contact = CONTACTS.get_contact_by_email("testingapis@hubspot.com")
    assert _is_contact(contact)


def test_get_contact_by_id():
    """
    attempts to fetch a contact via id
    :see: https://developers.hubspot.com/docs/methods/contacts/get_contact_by_id
    """
    with pytest.raises(HubspotNotFound):
        contact = CONTACTS.get_contact_by_id("-1")

    contact = CONTACTS.get_contact_by_id("11814674")
    assert _is_contact(contact)


def test_get_all():
    """
    tests getting all contacts
    :see: https://developers.hubspot.com/docs/methods/contacts/get_contacts
    """
    contacts = CONTACTS.get_all(limit=200)
    assert contacts
    assert len(contacts) <= 200
    assert contacts[0]
    assert contacts[0]["firstname"]
    assert contacts[0]["lastname"]
    assert contacts[0]["email"]
