"""
hubspot owners api
"""
from hubspot3.crm_associations import CRMAssociationsClient
from hubspot3.base import BaseClient


OWNERS_API_VERSION = "v2"


class OwnersClient(BaseClient):
    """
    hubspot3 Owners client
    :see: https://developers.hubspot.com/docs/methods/owners/owners_overview
    """

    def _get_path(self, subpath):
        """get the full api url for the given subpath on this client"""
        return "owners/{}/owners".format(OWNERS_API_VERSION)

    def get_owners(self, **options):
        """Only returns the list of owners, does not include additional metadata"""
        return self._call("owners", **options)

    def get_owner_name_by_id(self, owner_id: str, **options) -> str:
        """Given an id of an owner, return their name"""
        owner_name = "value_missing"
        owners = self.get_owners(**options)
        for owner in owners:
            if int(owner["ownerId"]) == int(owner_id):
                owner_name = "{} {}".format(owner["firstName"], owner["lastName"])
        return owner_name

    def get_owner_email_by_id(self, owner_id: str, **options) -> str:
        """given an id of an owner, return their email"""
        owner_email = "value_missing"
        owner = self.get_owner_by_id(owner_id, **options)
        if owner:
            owner_email = owner["email"]
        return owner_email

    def get_owner_by_id(self, owner_id, **options):
        """Retrieve an owner by its id."""
        owners = self.get_owners(**options)
        for owner in owners:
            if int(owner["ownerId"]) == int(owner_id):
                return owner
        return None

    def get_owner_by_email(self, owner_email, **options):
        """
        Retrieve an owner by its email.
        """
        owners = self.get_owners(method="GET", params={"email": owner_email}, **options)
        if owners:
            return owners[0]
        return None

    def link_owner_to_company(self, owner_id, company_id):
        """
        Link an owner to a company by using their ids.
        """
        associations_client = CRMAssociationsClient(**self.credentials)
        return associations_client.link_owner_to_company(owner_id, company_id)
