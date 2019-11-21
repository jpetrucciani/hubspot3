"""
hubspot companies api
"""
from hubspot3.base import BaseClient
from hubspot3.utils import prettify, get_log
from typing import List, Dict, Optional, Union


COMPANIES_API_VERSION = "2"


class CompaniesClient(BaseClient):
    """
    hubspot3 Companies client
    :see: https://developers.hubspot.com/docs/methods/companies/companies-overview
    """

    def __init__(self, *args, **kwargs):
        super(CompaniesClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.companies")

    def _get_path(self, subpath: str) -> str:
        """get the full api url for the given subpath on this client"""
        return "companies/v{}/{}".format(
            self.options.get("version") or COMPANIES_API_VERSION, subpath
        )

    def create(self, data: Dict = None, **options) -> Dict:
        """create a new company"""
        data = data or {}
        return self._call("companies/", data=data, method="POST", **options)

    def update(self, company_id: str, data: Dict = None, **options) -> Dict:
        """update the given company with data"""
        data = data or {}
        return self._call(
            "companies/{}".format(company_id), data=data, method="PUT", **options
        )

    def delete(self, company_id: str, **options) -> Dict:
        """delete a company"""
        return self._call("companies/{}".format(company_id), method="DELETE", **options)

    def delete_all(self, **options):
        """
        Delete all the companies. Please use it carefully.
        """
        for company in self.get_all(**options):
            self.delete(company["id"])

    def get(self, company_id: str, **options) -> Dict:
        """get a single company by it's ID"""
        return self._call("companies/{}".format(company_id), method="GET", **options)

    def search_domain(
        self, domain: str, limit: int = 1, extra_properties: Dict = None, **options
    ) -> Dict:
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
            **options
        )

    def get_all(
        self,
        prettify_output: bool = True,
        extra_properties: Union[str, List] = None,
        **options
    ) -> Optional[List]:
        """
        get all companies, including extra properties if they are passed in
        :see: https://developers.hubspot.com/docs/methods/deals/get-all-deals
        """
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
                    "propertiesWithHistory": properties,
                    "includeMergeAudits": "true",
                },
                **options
            )
            output.extend(
                [
                    prettify(company, id_key="companyId")
                    if prettify_output
                    else company
                    for company in batch["companies"]
                    if not company["isDeleted"]
                ]
            )
            finished = not batch["has-more"]
            offset = batch["offset"]

        return output

    def _get_recent(
        self,
        recency_type: str,
        limit: int = 250,
        offset: int = 0,
        since: int = None,
        **options
    ) -> Optional[List]:
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

        while not finished:
            params = {"count": limit, "offset": offset}
            if since:
                params["since"] = since
            batch = self._call(
                "companies/recent/{}".format(recency_type),
                method="GET",
                doseq=True,
                params=params,
                **options
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

    def get_recently_modified(
        self, limit: int = 250, offset: int = 0, since: int = None, **options
    ) -> Optional[List]:
        """
        returns all of the recently modified deals
        :see: https://developers.hubspot.com/docs/methods/deals/get_deals_modified
        """
        return self._get_recent(
            "modified", limit=limit, offset=offset, since=since, **options
        )

    def get_recently_created(
        self, limit: int = 250, offset: int = 0, since: int = None, **options
    ) -> Optional[List]:
        """
        returns all of the recently created deals
        :see: https://developers.hubspot.com/docs/methods/deals/get_deals_created
        """
        return self._get_recent(
            "created", limit=limit, offset=offset, since=since, **options
        )

    def get_contacts_at_a_company(self, company_id: str, **options) -> Optional[List]:
        """
        returns all of the contacts who have an associatedcompanyid contact property of
        `company_id`.

        :see: https://developers.hubspot.com/docs/methods/companies/get_company_contacts
        """
        return self._call(
            "companies/{}/contacts".format(company_id), method="GET", **options
        )
