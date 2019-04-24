"""
hubspot companies api
"""
from hubspot3 import logging_helper
from hubspot3.base import BaseClient
from hubspot3.utils import prettify
from typing import List, Mapping, Optional, Union


COMPANIES_API_VERSION = "2"


class CompaniesClient(BaseClient):
    """
    hubspot3 Companies client
    :see: https://developers.hubspot.com/docs/methods/companies/companies-overview
    """

    def __init__(self, *args, **kwargs):
        super(CompaniesClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.companies")

    def _get_path(self, subpath: str) -> str:
        """get the full api url for the given subpath on this client"""
        return "companies/v{}/{}".format(
            self.options.get("version") or COMPANIES_API_VERSION, subpath
        )

    def create(self, data: Mapping = None, **options) -> Mapping:
        """create a new company"""
        data = data or {}
        return self._call("companies/", data=data, method="POST", **options)

    def update(self, company_id: str, data: Mapping = None, **options) -> Mapping:
        """update the given company with data"""
        data = data or {}
        return self._call(
            "companies/{}".format(company_id), data=data, method="PUT", **options
        )

    def delete(self, company_id: str, **options) -> Mapping:
        """delete a company"""
        return self._call("companies/{}".format(company_id), method="DELETE", **options)

    def get(self, company_id: str, **options) -> Mapping:
        """get a single company by it's ID"""
        return self._call("companies/{}".format(company_id), method="GET", **options)

    def search_domain(
        self, domain: str, limit: int = 1, extra_properties: Mapping = None, **options
    ) -> Mapping:
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

    def get_all(
        self, extra_properties: Union[str, List] = None, **options
    ) -> Optional[List]:
        """get all companies, including extra properties if they are passed in"""
        finished = False
        output = []
        offset = 0
        query_limit = 250  # Max value according to docs

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
                    "limit": query_limit,
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

    def _get_recent(self, recency_type: str, **options) -> Optional[List]:
        """
        Returns either list of recently modified companies or recently created companies,
        depending on recency_type passed in. Both API endpoints take identical parameters
        and return identical formats, they differ only in the URLs
        (companies/recent/created or companies/recent/modified)
        :see: https://developers.hubspot.com/docs/methods/companies/get_companies_modified
        :see: https://developers.hubspot.com/docs/methods/companies/get_companies_created
        """
        finished = False
        output = []
        offset = 0
        query_limit = 250  # Max value according to docs

        while not finished:
            batch = self._call(
                "companies/recent/{}".format(recency_type),
                method="GET",
                doseq=True,
                params={"count": query_limit, "offset": offset},
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

    def get_recently_modified(self, **options) -> Optional[List]:
        return self._get_recent("modified", **options)

    def get_recently_created(self, **options) -> Optional[List]:
        return self._get_recent("created", **options)

    def get_contacts_at_a_company(self, company_id: str, **options) -> Optional[List]:
        """
        Returns all of the contacts who have an associatedcompanyid contact property of
        `company_id`.

        :see: https://developers.hubspot.com/docs/methods/companies/get_company_contacts
        """
        return self._call(
            "companies/{}/contacts".format(company_id), method="GET", **options
        )
