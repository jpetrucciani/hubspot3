"""
testing hubspot3.contacts
"""
import pytest
from hubspot3.contacts import ContactsClient
from hubspot3.error import HubspotConflict, HubspotNotFound, HubspotBadRequest
from hubspot3.test.globals import TEST_KEY


CONTACTS = ContactsClient(TEST_KEY)

# since we need to have an id to submit and to attempt to get a contact,
# we need to be hacky here and fetch one upon loading this file.
BASE_CONTACT = CONTACTS.get_all(limit=1)[0]


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
                    {"property": "email", "value": BASE_CONTACT["email"]},
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
    assert contact["vid"]
    assert contact["properties"]
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

    # since their demo data api doesn't seem stable, attempt to find one
    contact = CONTACTS.get_contact_by_email("testingapis@hubspot.com")
    contact_check = CONTACTS.get_contact_by_id(contact["vid"])
    assert _is_contact(contact)
    assert _is_contact(contact_check)


def test_get_all():
    """
    tests getting all contacts
    :see: https://developers.hubspot.com/docs/methods/contacts/get_contacts
    """
    contacts = CONTACTS.get_all(limit=20)
    assert contacts
    assert len(contacts) <= 20
    assert contacts[0]
    assert contacts[0]["email"]
    assert contacts[0]["id"]


def test_get_recently_created():
    """
    gets recently created deals
    :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_created_contacts
    """
    new_contacts = CONTACTS.get_recently_created(limit=20)
    assert new_contacts
    assert len(new_contacts) <= 20
    assert _is_contact(new_contacts[0])


def test_get_recently_modified():
    """
    gets recently modified deals
    :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_updated_contacts
    """
    modified_contacts = CONTACTS.get_recently_created(limit=20)
    assert modified_contacts
    assert len(modified_contacts) <= 20
    assert _is_contact(modified_contacts[0])
