"""
testing hubspot3.contacts
"""
import warnings
from unittest.mock import Mock

import pytest

from hubspot3 import contacts


@pytest.fixture
def contacts_client(mock_connection):
    client = contacts.ContactsClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


class TestContactsClient(object):
    def test_get_path(self):
        client = contacts.ContactsClient(disable_auth=True)
        subpath = "contact"
        assert client._get_path(subpath) == "contacts/v1/contact"

    def test_create_or_update_by_email(self, contacts_client, mock_connection):
        email = "mail@email.com"
        data = {"properties": [{"property": "firstname", "value": "hub"}]}
        response_body = {"isNew": False, "vid": 3234574}
        mock_connection.set_response(200, response_body)
        resp = contacts_client.create_or_update_by_email(email, data)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "POST", "/contacts/v1/contact/createOrUpdate/email/{}?".format(email), data
        )
        assert resp == response_body

    def test_get_by_email(self, contacts_client, mock_connection):
        email = "mail@email.com"
        response_body = {
            "vid": 3234574,
            "canonical-vid": 3234574,
            "merged-vids": [],
            "portal-id": 62515,
            "is-contact": True,
            "profile-token": "AO_T-m",
            "profile-url": "https://app.hubspot.com/contacts/62515/lists/public/contact/_AO_T-m/",
            "properties": {},
        }
        mock_connection.set_response(200, response_body)
        resp = contacts_client.get_by_email(email)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "GET", "/contacts/v1/contact/email/{}/profile?".format(email)
        )
        assert resp == response_body

    def test_get_by_id(self, contacts_client, mock_connection):
        vid = "234"
        response_body = {
            "vid": 3234574,
            "canonical-vid": 3234574,
            "merged-vids": [],
            "portal-id": 62515,
            "is-contact": True,
            "profile-token": "AO_T-m",
            "profile-url": "https://app.hubspot.com/contacts/62515/lists/public/contact/_AO_T-m/",
            "properties": {},
        }
        mock_connection.set_response(200, response_body)
        resp = contacts_client.get_by_id(vid)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "GET", "/contacts/v1/contact/vid/{}/profile?".format(vid)
        )
        assert resp == response_body

    def test_update_by_id(self, contacts_client, mock_connection):
        contact_id = "234"
        data = {"properties": [{"property": "firstname", "value": "hub"}]}
        response_body = ""
        mock_connection.set_response(204, response_body)
        resp = contacts_client.update_by_id(contact_id, data)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "POST", "/contacts/v1/contact/vid/{}/profile?".format(contact_id), data
        )
        assert resp == response_body

    def test_delete_by_id(self, contacts_client, mock_connection):
        contact_id = "234"
        response_body = {"vid": contact_id, "deleted": True, "reason": "OK"}
        mock_connection.set_response(204, response_body)
        resp = contacts_client.delete_by_id(contact_id)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "DELETE", "/contacts/v1/contact/vid/{}?".format(contact_id)
        )
        assert resp == response_body

    def test_create(self, contacts_client, mock_connection):
        data = {"properties": [{"property": "email", "value": "hub@spot.com"}]}
        response_body = {
            "identity-profiles": [
                {
                    "identities": [
                        {
                            "timestamp": 1331075050646,
                            "type": "EMAIL",
                            "value": "fumanchu@hubspot.com",
                        },
                        {
                            "timestamp": 1331075050681,
                            "type": "LEAD_GUID",
                            "value": "22a26060-c9d7-44b0-9f07-aa40488cfa3a",
                        },
                    ],
                    "vid": 61574,
                }
            ],
            "properties": {},
        }
        mock_connection.set_response(200, response_body)
        resp = contacts_client.create(data)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request("POST", "/contacts/v1/contact?", data)
        assert resp == response_body

    def test_update_by_email(self, contacts_client, mock_connection):
        email = "mail@email.com"
        data = {"properties": [{"property": "firstname", "value": "hub"}]}
        response_body = ""
        mock_connection.set_response(204, response_body)
        resp = contacts_client.update_by_email(email, data)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "POST", "/contacts/v1/contact/email/{}/profile?".format(email), data
        )
        assert resp == response_body

    def test_merge(self, contacts_client, mock_connection):
        primary_id, secondary_id = 10, 20
        mock_connection.set_response(200, "SUCCESS")
        resp = contacts_client.merge(primary_id, secondary_id)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "POST",
            "/contacts/v1/contact/merge-vids/{}/?".format(primary_id),
            dict(vidToMerge=secondary_id),
        )
        assert resp is None

    @pytest.mark.parametrize(
        "limit, query_limit, extra_properties",
        [
            (0, 100, None),
            (10, 10, None),
            (20, 20, None),
            (150, 100, None),  # keep query limit at max 100
            (10, 10, ["hs_analytics_last_url", "hs_analytics_revenue"]),
            (10, 10, "lead_source"),
        ],
    )
    def test_get_all(
        self, contacts_client, mock_connection, limit, query_limit, extra_properties
    ):
        response_body = {
            "contacts": [
                {
                    "addedAt": 1390574181854,
                    "vid": 204727,
                    "canonical-vid": 204727,
                    "merged-vids": [],
                    "properties": {},
                }
            ],
            "has-more": False,
            "vid-offset": 204727,
        }
        get_batch_return = [dict(id=204727 + i) for i in range(30)]
        get_batch_mock = Mock(return_value=get_batch_return)
        contacts_client.get_batch = get_batch_mock
        mock_connection.set_response(200, response_body)
        resp = contacts_client.get_all(limit=limit, extra_properties=extra_properties)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "GET",
            "/contacts/v1/lists/all/contacts/all?count={}&vidOffset=0".format(
                query_limit
            ),
        )
        assert resp == get_batch_return if not limit else get_batch_return[:limit]
        get_batch_mock.assert_called_once_with(
            [contact["vid"] for contact in response_body["contacts"]],
            extra_properties=extra_properties,
        )

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
        self,
        contacts_client,
        mock_connection,
        extra_properties_given,
        extra_properties_as_list,
    ):
        response_body = {
            "3234574": {"vid": 3234574, "canonical-vid": 3234574, "properties": {}},
            "3234575": {"vid": 3234575, "canonical-vid": 3234575, "properties": {}},
        }
        ids = ["3234574", "3234575"]
        properties = contacts_client.default_batch_properties.copy()
        properties.extend(extra_properties_as_list)
        query_properties = ["property={}".format(p) for p in properties]
        vids = ["vid={}".format(vid) for vid in ids]
        params = vids
        params.extend(query_properties)

        mock_connection.set_response(200, response_body)
        resp = contacts_client.get_batch(ids, extra_properties_given)
        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "GET", "/contacts/v1/contact/vids/batch?{}".format("&".join(params))
        )
        assert resp == [{"id": 3234574}, {"id": 3234575}]


class TestDeprecatedMethods(object):

    contact_id = "1"
    email = "test@example.com"
    options = dict(x="y")
    data = dict(z="23")

    @staticmethod
    def _check_deprecation_warning(warning_instance, old_name, new_name):
        assert len(warning_instance) == 1
        assert issubclass(warning_instance[-1].category, DeprecationWarning)
        message = str(warning_instance[-1].message)
        assert "{old_name} is deprecated".format(old_name=old_name) in message
        assert new_name in message

    def test_create_or_update_contact_by_email(self, contacts_client):
        create_or_update_contact_by_email_mock = Mock()
        contacts_client.create_or_update_by_email = (
            create_or_update_contact_by_email_mock
        )
        with warnings.catch_warnings(record=True) as w:
            contacts_client.create_or_update_a_contact(
                self.email, self.data, **self.options
            )
        self._check_deprecation_warning(
            w,
            old_name="create_or_update_a_contact",
            new_name="create_or_update_by_email",
        )
        create_or_update_contact_by_email_mock.assert_called_once_with(
            self.email, self.data, **self.options
        )

    def test_get_contact_by_email(self, contacts_client):
        get_by_email_mock = Mock()
        contacts_client.get_by_email = get_by_email_mock
        with warnings.catch_warnings(record=True) as w:
            contacts_client.get_contact_by_email(self.email, **self.options)
        self._check_deprecation_warning(
            w, old_name="get_contact_by_email", new_name="get_by_email"
        )
        get_by_email_mock.assert_called_once_with(self.email, **self.options)

    def test_get_contact_by_id(self, contacts_client):
        get_by_id_mock = Mock()
        contacts_client.get_by_id = get_by_id_mock
        with warnings.catch_warnings(record=True) as w:
            contacts_client.get_contact_by_id(self.contact_id, **self.options)
        self._check_deprecation_warning(
            w, old_name="get_contact_by_id", new_name="get_by_id"
        )
        get_by_id_mock.assert_called_once_with(self.contact_id, **self.options)

    def test_delete_a_contact(self, contacts_client):
        delete_by_id_mock = Mock()
        contacts_client.delete_by_id = delete_by_id_mock
        with warnings.catch_warnings(record=True) as w:
            contacts_client.delete_a_contact(self.contact_id, **self.options)
        self._check_deprecation_warning(
            w, old_name="delete_a_contact", new_name="delete_by_id"
        )
        delete_by_id_mock.assert_called_once_with(self.contact_id, **self.options)

    def test_update_a_contact(self, contacts_client):
        update_contact_by_id_mock = Mock()
        contacts_client.update_by_id = update_contact_by_id_mock
        with warnings.catch_warnings(record=True) as w:
            contacts_client.update_a_contact(self.contact_id, self.data, **self.options)
        self._check_deprecation_warning(
            w, old_name="update_a_contact", new_name="update_by_id"
        )
        update_contact_by_id_mock.assert_called_once_with(
            self.contact_id, self.data, **self.options
        )

    def test_update(self, contacts_client):
        update_contact_by_id_mock = Mock()
        contacts_client.update_by_id = update_contact_by_id_mock
        with warnings.catch_warnings(record=True) as w:
            contacts_client.update(self.contact_id, self.data, **self.options)
        self._check_deprecation_warning(w, old_name="update", new_name="update_by_id")
        update_contact_by_id_mock.assert_called_once_with(
            self.contact_id, self.data, **self.options
        )
