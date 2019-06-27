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

    class Recency:
        """recency type enum"""

        CREATED = "created"
        MODIFIED = "modified"

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

    def update_contact_by_email(self, email: str, data=None, **options):
        """update the concat for the given email address with the given data"""
        data = data or {}

        return self._call(
            "contact/email/{}/profile".format(email),
            data=data,
            method="POST",
            **options
        )

    def merge_contacts(self, merge_into_contact_id: int, merge_from_contact_id: int,
                       **options):
        """
        merge the data from the merge_from_contact_id into the data of the
        merge_into_contact_id
        """
        data = dict(vidToMerge=merge_from_contact_id)

        return self._call(
            "contact/merge-vids/{}/".format(merge_into_contact_id),
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
        if limited and limit < query_limit:
            query_limit = limit
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

    def _get_recent(
        self,
        recency_type: str,
        limit: int = 100,
        vid_offset: int = 0,
        time_offset: int = 0,
        **options
    ):
        """
        returns a list of either recently created or recently modified/created contacts
        """
        finished = False
        output = []
        query_limit = 100  # max according to the docs
        recency_string = (
            "all"
            if recency_type == ContactsClient.Recency.CREATED
            else "recently_updated"
        )
        limited = limit > 0
        if limited and limit < query_limit:
            query_limit = limit

        while not finished:
            params = {"count": query_limit}
            if vid_offset and time_offset:
                params["vidOffset"] = vid_offset
                params["timeOffset"] = time_offset
            batch = self._call(
                "lists/{}/contacts/recent".format(recency_string),
                method="GET",
                params=params,
                doseq=True,
                **options
            )
            output.extend([contact for contact in batch["contacts"]])
            finished = not batch["has-more"] or len(output) >= limit
            vid_offset = batch["vid-offset"]
            time_offset = batch["time-offset"]

        return output[:limit]

    def get_recently_created(self, limit: int = 100):
        """
        get recently created contacts
        :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_created_contacts
        """
        return self._get_recent(ContactsClient.Recency.CREATED, limit=limit)

    def get_recently_modified(self, limit: int = 100):
        """
        get recently modified and created contacts
        :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_updated_contacts
        """
        return self._get_recent(ContactsClient.Recency.MODIFIED, limit=limit)
