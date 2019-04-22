"""
hubspot associations api
"""
from hubspot3 import logging_helper
from hubspot3.base import BaseClient
from hubspot3.globals import (
    ASSOCIATION_TYPE_CONTACT_TO_COMPANY,
    ASSOCIATION_TYPE_LINE_ITEM_TO_DEAL,
    ASSOCIATION_TYPE_OWNER_TO_COMPANY,
    VALID_ASSOCIATION_TYPES,
)


ASSOCIATIONS_API_VERSION = '1'

ASSOCIATION_CATEGORY = 'HUBSPOT_DEFINED'  # see: https://developers.hubspot.com/docs/methods/crm-associations/associate-objects  # noqa

ASSOCIATION_DEFINITION_COMPANY_TO_CONTACT = 'company_to_contact'
ASSOCIATION_DEFINITION_COMPANY_TO_DEAL = 'company_to_deal'
ASSOCIATION_DEFINITION_DEAL_TO_LINE = 'deal_to_line_item'

# Cf: https://developers.hubspot.com/docs/methods/crm-associations/crm-associations-overview
ASSOCIATION_DEFINITIONS = {
    ASSOCIATION_DEFINITION_COMPANY_TO_CONTACT: 2,
    ASSOCIATION_DEFINITION_COMPANY_TO_DEAL: 6,
    ASSOCIATION_DEFINITION_DEAL_TO_LINE: 19,
}


class AssociationsClient(BaseClient):
    """
    The hubspot3 Associations client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json return
    """

    def __init__(self, *args, **kwargs):
        super(AssociationsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hapi.properties")

    def _get_path(self, subpath):
        return "crm-associations/v{}/associations/{}".format(
            ASSOCIATIONS_API_VERSION,
            subpath,
        )

    def create(self, association_type, from_object_id, to_object_id):
        if association_type not in VALID_ASSOCIATION_TYPES:
            raise ValueError(
                "Invalid association type. Valid association types are: {}".format(
                    VALID_ASSOCIATION_TYPES
                )
            )

        return self._call(
            "", method="PUT", data={
                "category": ASSOCIATION_CATEGORY,
                "definitionId": association_type,
                "fromObjectId": from_object_id,
                "toObjectId": to_object_id,
            }
        )

    def get_association_for_crm_object(self, object_id, definition_id, params, **options):
        """
        Get the IDs of objects associated with the given object, based on the specified association
        type.

        See the [association table](https://developers.hubspot.com/docs/methods/crm-associations/crm-associations-overview)  # noqa
        to know which `definition_id` to use.

        Example:
        ```
        https://api.hubapi.com/crm-associations/v1/associations/25/HUBSPOT_DEFINED/15?hapikey=demo
        ```

        Parameters
        ----------
        object_id
        definition_id
        params

        Returns
        -------
        list of ids
        """
        params = params or {}

        finished = False
        offset = 0
        output = []

        while not finished:
            try:
                _params = {
                    **params,
                    "offset": offset
                }
            except TypeError:
                # params is probably a tuple instance.
                _params = params
                _params.append(('offset', offset))

            batch = self._call(
                '{object_id}/{association_category}/{definition_id}'.format(
                    object_id=object_id,
                    association_category=ASSOCIATION_CATEGORY,
                    definition_id=definition_id,
                ),
                method='GET',
                params=_params,
                **options,
            )
            finished = not batch['hasMore']
            offset = batch['offset']
            output += batch['results']

        return output

    def get_deal_to_lines_items(self, deal_id, params=None, **options):
        """
        Get the lines related to a deal.
        """
        return self.get_association_for_crm_object(
            object_id=deal_id,
            params=params,
            definition_id=ASSOCIATION_DEFINITIONS[ASSOCIATION_DEFINITION_DEAL_TO_LINE],
            **options,
        )

    def get_company_to_contacts(self, company_id, params=None, **options):
        """Get the contacts related to a company."""
        return self.get_association_for_crm_object(
            object_id=company_id,
            params=params,
            definition_id=ASSOCIATION_DEFINITIONS[ASSOCIATION_DEFINITION_COMPANY_TO_CONTACT],
            **options,
        )

    def get_company_to_deals(self, company_id, params=None, **options):
        """Get the deals related to a company."""
        return self.get_association_for_crm_object(
            object_id=company_id,
            params=params,
            definition_id=ASSOCIATION_DEFINITIONS[ASSOCIATION_DEFINITION_COMPANY_TO_DEAL],
            **options,
        )

    def link_line_item_to_deal(self, line_item_id, deal_id):
        return self.create(
            ASSOCIATION_TYPE_LINE_ITEM_TO_DEAL,
            line_item_id,
            deal_id,
        )

    def link_contact_to_company(self, contact_id, company_id):
        return self.create(ASSOCIATION_TYPE_CONTACT_TO_COMPANY, contact_id, company_id)

    def link_owner_to_company(self, owner_id, company_id):
        return self.create(
            ASSOCIATION_TYPE_OWNER_TO_COMPANY,
            owner_id,
            company_id,
        )
