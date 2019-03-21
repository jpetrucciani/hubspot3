"""
hubspot companies api
"""
from hubspot3 import logging_helper
from hubspot3.base import BaseClient
from hubspot3.utils import prettify


COMPANIES_API_VERSION = "2"


class CompaniesClient(BaseClient):
    """
    The hubspot3 Companies client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json return
    """

    def __init__(self, *args, **kwargs):
        super(CompaniesClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.companies")

    def _get_path(self, subpath):
        return "companies/v{}/{}".format(
            self.options.get("version") or COMPANIES_API_VERSION, subpath
        )

    def create(self, data=None, **options):
        """create a new company"""
        data = data or {}
        return self._call("companies/", data=data, method="POST", **options)

    def update(self, company_id, data=None, **options):
        """update the given company with data"""
        data = data or {}
        return self._call(
            "companies/{}".format(company_id), data=data, method="PUT", **options
        )

    def delete(self, company_id, **options):
        """delete a company"""
        return self._call("companies/{}".format(company_id), method="DELETE", **options)

    def get(self, company_id, **options):
        """get a single company by it's ID"""
        return self._call("companies/{}".format(company_id), method="GET", **options)

    def search_domain(self, domain, limit=1, extra_properties=None, **options):
        """searches for companies by domain name. limit is max'd at 100"""
        # default properties to fetch
        properties = [
            "domain",
            "createdate",
            "name",
            "hs_lastmodifieddate",
            "hubspot_owner_id",
        ]

        # append extras if they exist
        if extra_properties:
            if isinstance(extra_properties, list):
                properties += extra_properties
            if isinstance(extra_properties, str):
                properties.append(extra_properties)

        return self._call(
            "domains/{}/companies".format(domain),
            method="POST",
            data={"limit": limit, "requestOptions": {"properties": properties}},
            **options,
        )

    def get_all(self, extra_properties=None, **options):
        finished = False
        output = []
        offset = 0
        querylimit = 250  # Max value according to docs

        # default properties to fetch
        properties = [
            "name",
            "description",
            "address",
            "address2",
            "city",
            "state",
            "story",
            "hubspot_owner_id",
        ]

        # append extras if they exist
        if extra_properties:
            if isinstance(extra_properties, list):
                properties += extra_properties
            if isinstance(extra_properties, str):
                properties.append(extra_properties)

        while not finished:
            batch = self._call(
                "companies/paged",
                method="GET",
                doseq=True,
                params={
                    "limit": querylimit,
                    "offset": offset,
                    "properties": properties,
                },
                **options,
            )
            output.extend(
                [
                    prettify(company, id_key="companyId")
                    for company in batch["companies"]
                    if not company["isDeleted"]
                ]
            )
            finished = not batch["has-more"]
            offset = batch["offset"]

        return output

    def _get_recent(self, recency_type, **options):
        """
          Returns either list of recently modified companies or recently created companies, depending on
          recency_type passed in. Both API endpoints take identical parameters and return identical formats,
          they differ only in the URLs (companies/recent/created or companies/recent/modified)
          @see: https://developers.hubspot.com/docs/methods/companies/get_companies_modified
          @see: https://developers.hubspot.com/docs/methods/companies/get_companies_created
        """
        finished = False
        output = []
        offset = 0
        querylimit = 250  # Max value according to docs

        while not finished:
            batch = self._call(
                "companies/recent/%s" % recency_type,
                method="GET",
                doseq=True,
                params={"count": querylimit, "offset": offset},
                **options,
            )
            output.extend(
                [
                    prettify(company, id_key="companyId")
                    for company in batch["results"]
                    if not company["isDeleted"]
                ]
            )
            finished = not batch["hasMore"]
            offset = batch["offset"]

        return output

    def get_recently_modified(self, **options):
        return self._get_recent("modified", **options)

    def get_recently_created(self, **options):
        return self._get_recent("created", **options)
