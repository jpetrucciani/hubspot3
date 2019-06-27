"""
testing hubspot3.contacts
"""
import warnings
from unittest.mock import Mock

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

    contact = CONTACTS.get_contact_by_email(BASE_CONTACT["email"])
    assert _is_contact(contact)


def test_get_contact_by_id():
    """
    attempts to fetch a contact via id
    :see: https://developers.hubspot.com/docs/methods/contacts/get_contact_by_id
    """
    with pytest.raises(HubspotNotFound):
        contact = CONTACTS.get_contact_by_id("-1")

    # since their demo data api doesn't seem stable, attempt to find one
    contact = CONTACTS.get_contact_by_email(BASE_CONTACT["email"])
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


class TestDeprecatedMethods(object):

    contact_id = '1'
    email = 'test@example.com'
    options = dict(x='y')
    data = dict(z='23')

    @staticmethod
    def _check_deprecation_warning(warning_instance, old_name, new_name):
        assert len(warning_instance) == 1
        assert issubclass(warning_instance[-1].category, DeprecationWarning)
        message = str(warning_instance[-1].message)
        assert "{old_name} is deprecated".format(old_name=old_name) in message
        assert new_name in message

    def test_create_or_update_contact_by_email(self):
        create_or_update_contact_by_email_mock = Mock()
        CONTACTS.create_or_update_contact_by_email = create_or_update_contact_by_email_mock
        with warnings.catch_warnings(record=True) as w:
            CONTACTS.create_or_update_a_contact(self.email, self.data, **self.options)
        self._check_deprecation_warning(w, old_name='create_or_update_a_contact',
                                        new_name='create_or_update_contact_by_email')
        create_or_update_contact_by_email_mock.assert_called_once_with(self.email, self.data,
                                                                       **self.options)

    def test_delete_a_contact(self):
        delete_by_id_mock = Mock()
        CONTACTS.delete_by_id = delete_by_id_mock
        with warnings.catch_warnings(record=True) as w:
            CONTACTS.delete_a_contact(self.contact_id, **self.options)
        self._check_deprecation_warning(w, old_name='delete_a_contact', new_name='delete_by_id')
        delete_by_id_mock.assert_called_once_with(self.contact_id, **self.options)

    def test_update_a_contact(self):
        update_contact_by_id_mock = Mock()
        CONTACTS.update_contact_by_id = update_contact_by_id_mock
        with warnings.catch_warnings(record=True) as w:
            CONTACTS.update_a_contact(self.contact_id, self.data, **self.options)
        self._check_deprecation_warning(w, old_name='update_a_contact',
                                        new_name='update_contact_by_id')
        update_contact_by_id_mock.assert_called_once_with(self.contact_id, self.data,
                                                          **self.options)

    def test_update(self):
        update_contact_by_id_mock = Mock()
        CONTACTS.update_contact_by_id = update_contact_by_id_mock
        with warnings.catch_warnings(record=True) as w:
            CONTACTS.update(self.contact_id, self.data, **self.options)
        self._check_deprecation_warning(w, old_name='update', new_name='update_contact_by_id')
        update_contact_by_id_mock.assert_called_once_with(self.contact_id, self.data,
                                                          **self.options)
