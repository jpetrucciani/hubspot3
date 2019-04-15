"""
hubspot prospects client
"""
from hubspot3.base import BaseClient


PROSPECTS_API_VERSION = "v1"


class ProspectsClient(BaseClient):
    """
    Python client for the HubSpot Prospects API.
    This client provides convenience methods for the HubSpot Prospects API.
    It is a work in progress, and contributions are welcome.
    """

    def _get_path(self, subpath):
        """get the full api url for the given subpath on this client"""
        return "prospects/{}/{}".format(PROSPECTS_API_VERSION, subpath)

    def get_prospects(self, offset=None, orgoffset=None, limit=None):
        """
        Return the prospects for the current API key.

        Optionally start the result list at the given offset.

        Each member of the return list is a prospect element containing
        organizational information such as name and location.
        """
        params = {}
        if limit:
            params["count"] = limit

        if offset:
            params["timeOffset"] = offset
            params["orgOffset"] = orgoffset

        return self._call("timeline", params)

    def get_company(self, company_slug):
        """Return the specific named organization for the given API key, if we find a match."""
        return self._call("timeline/{}".format(company_slug))

    def get_options_for_query(self, query):
        """This method allows for discovery of prospects with partial names."""
        return self._call("typeahead/", {"q": query})

    def search_prospects(self, search_type, query, offset=None, orgoffset=None):
        """
        Supports doing a search for prospects by city, reion, or country.

        search_type should be one of 'city' 'region' 'country'.

        This method is intended to be called with one of the outputs from the
        get_options_for_query method above.
        """
        params = {"q": query}
        if offset and orgoffset:
            params["orgOffset"] = orgoffset
            params["timeOffset"] = offset

        return self._call("search/{}".format(search_type), params)

    def get_hidden_prospects(self):
        """Return the list of prospects hidden by the customer (or this API), if any."""
        return self._call("filters")

    def hide_prospect(self, company_name):
        """Hides the given prospect from the user interface."""
        return self._call(
            "filters",
            data=("organization={}".format(company_name)),
            method="POST",
            content_type="application/x-www-form-urlencoded",
        )

    def unhide_prospect(self, company_name):
        """Un-hides, i.e. displays, the given prospect in the user interface."""
        return self._call(
            "filters", data={"organization": company_name}, method="DELETE"
        )
