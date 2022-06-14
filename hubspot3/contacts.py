"""
hubspot contacts api
"""
import warnings
from typing import Union
from hubspot3.crm_associations import CRMAssociationsClient
from hubspot3.base import BaseClient
from hubspot3.utils import clean_result, get_log, prettify

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

    def _get_path(self, subpath):
        """get path"""
        return "contacts/v{}/{}".format(CONTACTS_API_VERSION, subpath)

    def get_by_id(self, contact_id: str, **options):
        """Get contact specified by ID"""
        return self._call(
            "contact/vid/{}/profile".format(contact_id), method="GET", **options
        )

    def get_by_email(self, email, **options):
        """Get contact specified by email address."""
        return self._call(
            "contact/email/{email}/profile".format(email=email), method="GET", **options
        )

    def create(self, data=None, **options):
        """create a contact"""
        data = data or {}
        return self._call("contact", data=data, method="POST", **options)

    def create_or_update_by_email(self, email, data=None, **options):
        """Create or Updates a client with the supplied data."""
        data = data or {}
        return self._call(
            "contact/createOrUpdate/email/{email}".format(email=email),
            data=data,
            method="POST",
            **options
        )

    def update_by_id(self, contact_id, data=None, **options):
        """Update the contact by contact_id with the given data."""
        data = data or {}
        return self._call(
            "contact/vid/{contact_id}/profile".format(contact_id=contact_id),
            data=data,
            method="POST",
            **options
        )

    def update_by_email(self, email: str, data=None, **options):
        """update the concat for the given email address with the given data"""
        data = data or {}

        return self._call(
            "contact/email/{}/profile".format(email),
            data=data,
            method="POST",
            **options
        )

    def delete_by_id(self, contact_id: str, **options):
        """Delete a contact by contact_id."""
        return self._call(
            "contact/vid/{contact_id}".format(contact_id=contact_id),
            method="DELETE",
            **options
        )

    def merge(self, primary_id: int, secondary_id: int, **options):
        """merge the data from the secondary_id into the data of the primary_id"""
        data = dict(vidToMerge=secondary_id)

        self._call(
            "contact/merge-vids/{}/".format(primary_id),
            data=data,
            method="POST",
            **options
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

    def get_batch(self, ids, extra_properties: Union[list, str] = None):
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
        extra_properties: Union[list, str] = None,
        limit: int = -1,
        list_id: str = "all",
        **options
    ) -> list:
        contacts_generator = self.get_all_as_generator(extra_properties, limit, list_id, **options)
        contacts_list = list(contacts_generator)

        return [prettify(contact, id_key="vid") for contact in contacts_list]

    def get_all_as_generator(
        self,
        extra_properties: Union[list, str] = None,
        limit: int = -1,
        list_id: str = "all",
        with_history: bool = False,
        **options
    ):
        """
        get all contacts in hubspot, fetching additional properties if passed in
        Can't get phone number from a get-all, so we just grab IDs and
        then have to make ANOTHER call in batches
        :see: https://developers.hubspot.com/docs/methods/contacts/get_contacts
        """
        if with_history:
            property_mode = "value_and_history"
        else:
            property_mode = "value_only"
        offset = 0
        query_limit = 100  # Max value according to docs
        limited = limit > 0
        if limited and limit < query_limit:
            query_limit = limit

        # default properties to fetch
        properties = set(self.default_batch_properties)

        # append extras if they exist
        if extra_properties:
            if isinstance(extra_properties, list):
                properties.update(extra_properties)
            if isinstance(extra_properties, str):
                properties.add(extra_properties)

        contacts_count = 0
        finished = False
        while not finished:
            batch = self._call(
                "lists/{}/contacts/all".format(list_id),
                method="GET",
                params={
                    "count": query_limit,
                    "vidOffset": offset,
                    "property": properties,
                    "propertyMode": property_mode},
                doseq=True,
                **options
            )
            contacts = batch["contacts"]
            contacts_count += len(contacts)
            reached_limit = limited and contacts_count >= limit

            if reached_limit:
                contacts = contacts[:limit]

            finished = not batch["has-more"] or reached_limit
            offset = batch["vid-offset"]

            yield from contacts

    def _get_recent(
        self,
        recency_type: str,
        limit: int = 100,
        vid_offset: int = 0,
        time_offset: int = 0,
        **options
    ):
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

    def get_recently_modified_in_interval(
            self,
            start_date: int,  # data pull begin time
            end_date: int,  # data pull end time
            extra_properties: Union[list, str] = None,
            with_history: bool = False,
            query_limit: int = 100,
            form_submission_mode: str = "newest",
            **options
    ):
        """
        Return a list of either recently created or recently modified contacts by timestamp
        :see: https://developers.hubspot.com/docs/methods/contacts/get_recently_updated_contacts
        """
        finished = False

        default_properties = set(self.default_batch_properties)
        if extra_properties:
            if isinstance(extra_properties, list):
                default_properties.update(extra_properties)
            if isinstance(extra_properties, str):
                default_properties.add(extra_properties)

        if with_history:
            property_mode = "value_and_history"
        else:
            property_mode = "value_only"

        time_offset = end_date

        while not finished:
            params = {
                "count": query_limit,
                "property": default_properties,
                "timeOffset": time_offset,
                "propertyMode": property_mode,
                "formSubmissionMode": form_submission_mode}

            batch = self._call(
                "lists/recently_updated/contacts/recent",
                method="GET",
                params=params,
                doseq=True,
                **options
            )
            contacts = batch["contacts"]
            time_offset = batch["time-offset"]
            reached_time_limit = time_offset < start_date
            finished = not batch["has-more"] or reached_time_limit
            contacts = clean_result("contacts", contacts, start_date, end_date)

            yield from contacts

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

    def get_contact_by_id(self, contact_id: str, **options):
        warnings.warn(
            "ContactsClient.get_contact_by_id is deprecated in favor of "
            "ContactsClient.get_by_id",
            DeprecationWarning,
        )
        return self.get_by_id(contact_id, **options)

    def get_contact_by_email(self, email, **options):
        warnings.warn(
            "ContactsClient.get_contact_by_email is deprecated in favor of "
            "ContactsClient.get_by_email",
            DeprecationWarning,
        )
        return self.get_by_email(email, **options)

    def create_or_update_a_contact(self, email, data=None, **options):
        warnings.warn(
            "ContactsClient.create_or_update_a_contact is deprecated in favor of "
            "ContactsClient.create_or_update_by_email",
            DeprecationWarning,
        )
        return self.create_or_update_by_email(email, data, **options)

    def update(self, contact_id: str, data=None, **options):
        warnings.warn(
            "ContactsClient.update is deprecated in favor of "
            "ContactsClient.update_by_id",
            DeprecationWarning,
        )
        return self.update_by_id(contact_id, data, **options)

    def update_a_contact(self, contact_id, data=None, **options):
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

    def search(self, search_query, **options):
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

        output = []

        while not finished:
            batch = self._call(
                "search/query",
                method="GET",
                params={"count": query_limit, "offset": offset, "q": search_query},
                **options
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
            self.delete_a_contact(contact["vid"])
