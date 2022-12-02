"""
hubspot contacts api
"""
import warnings
from typing import Dict, List, Optional, Union
from hubspot3.crm_associations import CRMAssociationsClient
from hubspot3.base import BaseClient
from hubspot3.utils import prettify, get_log


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
        self.log = get_log("hubspot3.contacts")

    def _get_path(self, subpath: str) -> str:
        """get path"""
        return f"contacts/v{CONTACTS_API_VERSION}/{subpath}"

    def get_by_id(self, contact_id: str, **options):
        """Get contact specified by ID"""
        return self._call(f"contact/vid/{contact_id}/profile", method="GET", **options)

    def get_by_email(self, email: str, **options):
        """Get contact specified by email address."""
        return self._call(f"contact/email/{email}/profile", method="GET", **options)

    def create(self, data: Optional[Dict] = None, **options):
        """create a contact"""
        data = data or {}
        return self._call("contact", data=data, method="POST", **options)

    def create_or_update_by_email(
        self, email: str, data: Optional[Dict] = None, **options
    ):
        """Create or Updates a client with the supplied data."""
        data = data or {}
        return self._call(
            f"contact/createOrUpdate/email/{email}", data=data, method="POST", **options
        )

    def update_by_id(self, contact_id: str, data: Optional[Dict] = None, **options):
        """Update the contact by contact_id with the given data."""
        data = data or {}
        return self._call(
            f"contact/vid/{contact_id}/profile", data=data, method="POST", **options
        )

    def update_by_email(self, email: str, data=None, **options):
        """update the concat for the given email address with the given data"""
        data = data or {}

        return self._call(
            f"contact/email/{email}/profile", data=data, method="POST", **options
        )

    def delete_by_id(self, contact_id: str, **options):
        """Delete a contact by contact_id."""
        return self._call(f"contact/vid/{contact_id}", method="DELETE", **options)

    def merge(self, primary_id: int, secondary_id: int, **options):
        """merge the data from the secondary_id into the data of the primary_id"""
        data = dict(vidToMerge=secondary_id)

        self._call(
            f"contact/merge-vids/{primary_id}/", data=data, method="POST", **options
        )

    default_batch_properties = [
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

    def get_batch(self, ids, extra_properties: Union[List, str, None] = None):
        """given a batch of vids, get more of their info"""
        # default properties to fetch
        properties = set(self.default_batch_properties)

        # append extras if they exist
        if extra_properties:
            if isinstance(extra_properties, list):
                properties.update(extra_properties)
            if isinstance(extra_properties, str):
                properties.add(extra_properties)

        batch = self._call(
            "contact/vids/batch",
            method="GET",
            doseq=True,
            params={"vid": ids, "property": list(properties)},
        )
        # It returns a dict with IDs as keys
        return [prettify(batch[contact], id_key="vid") for contact in batch]

    def link_contact_to_company(self, contact_id, company_id):
        associations_client = CRMAssociationsClient(**self.credentials)
        return associations_client.link_contact_to_company(contact_id, company_id)

    def get_all(
        self,
        extra_properties: Union[List, str, None] = None,
        limit: int = -1,
        list_id: str = "all",
        **options,
    ) -> List[Dict]:
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
                f"lists/{list_id}/contacts/all",
                method="GET",
                params={"count": query_limit, "vidOffset": offset},
                **options,
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
        **options,
    ) -> List[Dict]:
        """
        return a list of either recently created or recently modified/created contacts
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
                f"lists/{recency_string}/contacts/recent",
                method="GET",
                params=params,
                doseq=True,
                **options,
            )
            output.extend([contact for contact in batch["contacts"]])
            finished = not batch["has-more"] or len(output) >= limit
            vid_offset = batch["vid-offset"]
            time_offset = batch["time-offset"]

        return output[:limit]

    def get_recently_created(self, limit: int = 100) -> List[Dict]:
        """
        get recently created contacts
        :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_created_contacts
        """
        return self._get_recent(ContactsClient.Recency.CREATED, limit=limit)

    def get_in_list(
        self,
        list_id: int,
        limit: int = 100,
        vid_offset: int = 0,
        time_offset: int = 0,
        **options,
    ) -> List[Dict]:
        """
        return contacts in a list
        """
        finished = False
        output = []
        query_limit = 100  # max according to the docs
        limited = limit > 0
        if limited and limit < query_limit:
            query_limit = limit

        while not finished:
            params = {"count": query_limit}
            if vid_offset and time_offset:
                params["vidOffset"] = vid_offset
                params["timeOffset"] = time_offset
            batch = self._call(
                f"lists/{list_id}/contacts/all",
                method="GET",
                params=params,
                doseq=True,
                **options,
            )
            output.extend([contact for contact in batch["contacts"]])
            finished = not batch["has-more"] or len(output) >= limit
            vid_offset = batch.get("vid-offset", 0)
            time_offset = batch.get("time-offset", 0)

        return output[:limit]

    def get_recently_modified(self, limit: int = 100) -> List[Dict]:
        """
        get recently modified and created contacts
        :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_updated_contacts
        """
        return self._get_recent(ContactsClient.Recency.MODIFIED, limit=limit)

    def get_contact_by_id(self, contact_id: str, **options):
        warnings.warn(
            "ContactsClient.get_contact_by_id is deprecated in favor of "
            "ContactsClient.get_by_id",
            DeprecationWarning,
        )
        return self.get_by_id(contact_id, **options)

    def get_contact_by_email(self, email: str, **options):
        warnings.warn(
            "ContactsClient.get_contact_by_email is deprecated in favor of "
            "ContactsClient.get_by_email",
            DeprecationWarning,
        )
        return self.get_by_email(email, **options)

    def create_or_update_a_contact(
        self, email: str, data: Optional[Dict] = None, **options
    ):
        warnings.warn(
            "ContactsClient.create_or_update_a_contact is deprecated in favor of "
            "ContactsClient.create_or_update_by_email",
            DeprecationWarning,
        )
        return self.create_or_update_by_email(email, data, **options)

    def update(self, contact_id: str, data: Optional[Dict] = None, **options):
        warnings.warn(
            "ContactsClient.update is deprecated in favor of "
            "ContactsClient.update_by_id",
            DeprecationWarning,
        )
        return self.update_by_id(contact_id, data, **options)

    def update_a_contact(self, contact_id: str, data: Optional[Dict] = None, **options):
        warnings.warn(
            "ContactsClient.update_a_contact is deprecated in favor of "
            "ContactsClient.update_by_id",
            DeprecationWarning,
        )
        return self.update_by_id(contact_id, data, **options)

    def delete_a_contact(self, contact_id: str, **options):
        warnings.warn(
            "ContactsClient.delete_a_contact is deprecated in favor of "
            "ContactsClient.delete_by_id",
            DeprecationWarning,
        )
        return self.delete_by_id(contact_id, **options)

    def search(self, search_query: str, **options):
        """
        Search among contacts for matches with the given `search_query`.

        Cf: https://developers.hubspot.com/docs/methods/contacts/search_contacts

        Parameters
        ----------
        search_query: str

        Returns
        -------
        list of dict
            The result of the search as a list of contacts.
        """
        finished = False
        offset = 0
        query_limit = 100  # Max value according to docs

        output = []  # type: list

        while not finished:
            batch = self._call(
                "search/query",
                method="GET",
                params={"count": query_limit, "offset": offset, "q": search_query},
                **options,
            )

            output += batch["contacts"]

            finished = not batch["has-more"]
            offset = batch["offset"]

        return output

    def delete_all(self):
        """
        Delete all the contacts. Please use it carefully.
        """
        for contact in self.get_all():
            self.delete_by_id(contact["vid"])
