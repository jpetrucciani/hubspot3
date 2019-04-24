"""
hubspot contacts api
"""
from hubspot3 import logging_helper
from hubspot3.base import BaseClient
from hubspot3.utils import prettify
from typing import Union


CONTACTS_API_VERSION = "1"


class ContactsClient(BaseClient):
    """
    The hubspot3 Contacts client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        """initialize a contacts client"""
        super(ContactsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.contacts")

    def _get_path(self, subpath):
        return "contacts/v{}/{}".format(CONTACTS_API_VERSION, subpath)

    def create_or_update_a_contact(self, email, data=None, **options):
        """Creates or Updates a client with the supplied data."""
        data = data or {}
        return self._call(
            "contact/createOrUpdate/email/{email}".format(email=email),
            data=data,
            method="POST",
            **options
        )

    def get_contact_by_email(self, email, **options):
        """Gets contact specified by email address."""
        return self._call(
            "contact/email/{email}/profile".format(email=email), method="GET", **options
        )

    def get_contact_by_id(self, contact_id: str, **options):
        """Gets contact specified by ID"""
        return self._call(
            "contact/vid/{}/profile".format(contact_id), method="GET", **options
        )

    def update_a_contact(self, contact_id, data=None, **options):
        """Updates the contact by contact_id with the given data."""
        data = data or {}
        return self._call(
            "contact/vid/{contact_id}/profile".format(contact_id=contact_id),
            data=data,
            method="POST",
            **options
        )

    def delete_a_contact(self, contact_id: str, **options):
        """Deletes a contact by contact_id."""
        return self._call(
            "contact/vid/{contact_id}".format(contact_id=contact_id),
            method="DELETE",
            **options
        )

    def create(self, data=None, **options):
        """create a contact"""
        data = data or {}
        return self._call("contact", data=data, method="POST", **options)

    def update(self, contact_id: str, data=None, **options):
        """update the given vid with the given data"""
        if not data:
            data = {}

        return self._call(
            "contact/vid/{}/profile".format(contact_id),
            data=data,
            method="POST",
            **options
        )

    def get_batch(self, ids, extra_properties: Union[list, str] = None):
        """given a batch of vids, get more of their info"""
        # default properties to fetch
        properties = [
            "email",
            "firstname",
            "lastname",
            "company",
            "website",
            "phone",
            "address",
            "city",
            "state",
            "zip",
            "associatedcompanyid",
        ]

        # append extras if they exist
        if extra_properties:
            if isinstance(extra_properties, list):
                properties += extra_properties
            if isinstance(extra_properties, str):
                properties.append(extra_properties)

        batch = self._call(
            "contact/vids/batch",
            method="GET",
            doseq=True,
            params={"vid": ids, "property": properties},
        )
        # It returns a dict with IDs as keys
        return [prettify(batch[contact], id_key="vid") for contact in batch]

    def get_all(
        self, extra_properties: Union[list, str] = None, limit: int = -1, **options
    ) -> list:
        """
        get all contacts in hubspot, fetching additional properties if passed in
        Can't get phone number from a get-all, so we just grab IDs and
        then have to make ANOTHER call in batches
        :see: https://developers.hubspot.com/docs/methods/contacts/get_contacts
        """
        finished = False
        output = []  # type: list
        offset = 0
        query_limit = 100  # Max value according to docs
        limited = limit > 0
        while not finished:
            batch = self._call(
                "lists/all/contacts/all",
                method="GET",
                params={"count": query_limit, "vidOffset": offset},
                **options
            )
            output.extend(
                self.get_batch(
                    [contact["vid"] for contact in batch["contacts"]],
                    extra_properties=extra_properties,
                )
            )
            finished = not batch["has-more"] or (limited and len(output) >= limit)
            offset = batch["vid-offset"]

        return output if not limited else output[:limit]
