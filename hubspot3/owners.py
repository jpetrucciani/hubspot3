"""
hubspot owners api
"""

from hubspot3.crm_associations import CRMAssociationsClient
from hubspot3.base import BaseClient


OWNERS_API_VERSION = "v3"


class OwnersClient(BaseClient):
    """
    hubspot3 Owners client
    :see: https://developers.hubspot.com/docs/methods/owners/owners_overview
    """

    def _get_path(self, subpath):
        """get the full api url for the given subpath on this client"""
        return f"crm/{OWNERS_API_VERSION}/owners"

    def get_owners(self, **options):
        """Only returns the list of owners, does not include additional metadata"""
        owners = []
        opts = dict(options)
        more = True
        while more:
            data = self._call("owners", **opts)
            owners.extend(data["results"][: opts["limit"]])
            opts["limit"] -= len(data["results"])
            if opts["limit"] < 1:
                more = False
            if "paging" in data:
                opts["after"] = data["paging"]["next"]["after"]
            else:
                more = False
        return owners

    def get_owner_name_by_id(self, owner_id: str, **options) -> str:
        """Given an id of an owner, return their name"""
        owner_name = "value_missing"
        owners = self._call(f"owners/{owner_id}", **options)
        if owners["results"]:
            owner = owners["results"][0]
            owner_name = f"{owner['firstName']} {owner['lastName']}"
        return owner_name

    def get_owner_email_by_id(self, owner_id: str, **options) -> str:
        """given an id of an owner, return their email"""
        owner_email = "value_missing"
        owners = self._call(f"owners/{owner_id}", **options)
        if owners["results"]:
            owner_email = owners["results"][0]["email"]
        return owner_email

    def get_owner_by_id(self, owner_id, **options):
        """Retrieve an owner by its id."""
        owners = self._call(f"owners/{owner_id}", **options)
        if owners["results"]:
            return owners["results"][0]
        return None

    def get_owner_by_email(self, owner_email: str, **options):
        """
        Retrieve an owner by its email.
        """
        owners = self.get_owners(method="GET", params={"email": owner_email}, **options)
        if owners["results"]:
            return owners["results"][0]
        return None

    def link_owner_to_company(self, owner_id, company_id):
        """
        Link an owner to a company by using their ids.
        """
        associations_client = CRMAssociationsClient(**self.credentials)
        return associations_client.link_owner_to_company(owner_id, company_id)
