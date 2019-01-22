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
        self.log = logging_helper.get_log("hapi.companies")

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
