"""
hubspot crm_association_labels api
"""
from enum import Enum
from typing import List, Dict, Optional, Union

from hubspot3.base import BaseClient
from hubspot3.utils import get_log

ASSOCIATIONS_API_VERSION = "4"


class ObjectTypeDefinitions(Enum):
    """see https://developers.hubspot.com/docs/api/crm/understanding-the-crm"""

    CONTACTS = "0-1"
    COMPANIES = "0-2"
    DEALS = "0-3"
    TICKETS = "0-5"
    CALLS = "0-48"
    EMAILS = "0-49"
    MEETINGS = "0-47"
    NOTES = "0-4"
    TASKS = "0-27"
    PRODUCTS = "0-7"
    LINE_ITEMS = "0-8"
    COMMUNICATIONS = "0-18"
    POSTAL_MAIL = "0-116"
    MARKETING_EVENTS = "0-54"
    FEEDBACK_SUBMISSIONS = "0-19"


class AssociationCategory(Enum):
    """see https://developers.hubspot.com/docs/cms/hubl/functions#crm-associations"""

    HUBSPOT_DEFINED = "HUBSPOT_DEFINED"
    USER_DEFINED = "USER_DEFINED"
    INTEGRATOR_DEFINED = "INTEGRATOR_DEFINED"


class CRMAssociationLabelsClient(BaseClient):
    """
    Association labels extension for Associations API v4 endpoint
    :see: https://developers.hubspot.com/docs/api/crm/associations
    """

    def __init__(self, *args, **kwargs):
        super(CRMAssociationLabelsClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.crm_association_labels")

    def _get_path(self, subpath: str) -> str:
        return (
            f'crm/v{self.options.get("version") or ASSOCIATIONS_API_VERSION}/{subpath}'
        )

    def list(
        self,
        from_object_type: ObjectTypeDefinitions,
        from_object_id: int,
        to_object_type: ObjectTypeDefinitions,
    ) -> List[Dict]:
        """
        List all association labels of an object by object type.
        """
        finished = False
        output = []
        after: Optional[str] = ""
        # 100 is max value according to docs, but "You can only request at most 500 associations
        # at once" error is thrown
        query_limit = 500

        while not finished:
            params: Dict[str, Union[int, str]] = {"limit": query_limit}
            if after:
                params["after"] = after
            batch = self._call(
                f"objects/{from_object_type.value}/{from_object_id}/"
                f"associations/{to_object_type.value}",
                method="GET",
                params=params,
            )
            output.extend([id_ for id_ in batch["results"]])
            if (
                "paging" in batch
                and "next" in batch["paging"]
                and "after" in batch["paging"]["next"]
            ):
                after = batch["paging"]["next"]["after"]
            else:
                after = None
            finished = not bool(after)

        return output

    def create_default(
        self,
        from_object_type: ObjectTypeDefinitions,
        from_object_id: int,
        to_object_type: ObjectTypeDefinitions,
        to_object_id: int,
        **options,
    ) -> Dict:
        """
        Create the default (most generic) association label between two object types
        """
        return self._call(
            f"objects/{from_object_type.value}/{from_object_id}/"
            f"associations/default/{to_object_type.value}/{to_object_id}",
            method="PUT",
            **options,
        )

    def create(
        self,
        from_object_type: ObjectTypeDefinitions,
        from_object_id: int,
        to_object_type: ObjectTypeDefinitions,
        to_object_id: int,
        association_category: AssociationCategory,
        association_type_id: int,
        **options,
    ) -> Dict:
        """
        Set association labels between two records.
        """
        return self._call(
            f"objects/{from_object_type.value}/{from_object_id}/"
            f"associations/{to_object_type.value}/{to_object_id}",
            method="PUT",
            data=[
                {
                    "associationCategory": association_category.value,
                    "associationTypeId": association_type_id,
                }
            ],
            **options,
        )

    def delete(
        self,
        from_object_type: ObjectTypeDefinitions,
        from_object_id: int,
        to_object_type: ObjectTypeDefinitions,
        to_object_id: int,
        **options,
    ) -> None:
        """
        Deletes all association labels between two records.
        """
        return self._call(
            f"objects/{from_object_type.value}/{from_object_id}/associations"
            f"/{to_object_type.value}/{to_object_id}",
            method="DELETE",
            **options,
        )

    def batch_list(self):
        raise NotImplementedError("Not implemented yet")

    def batch_create_default(self):
        raise NotImplementedError("Not implemented yet")

    def batch_create(self):
        raise NotImplementedError("Not implemented yet")

    def batch_delete(self):
        raise NotImplementedError("Not implemented yet")

    def batch_delete_specific(self):
        raise NotImplementedError("Not implemented yet")

    def read_schema(
        self,
        from_object_type: ObjectTypeDefinitions,
        to_object_type: ObjectTypeDefinitions,
    ) -> List[Dict]:
        """
        Returns all association label definitions between two object types
        """
        results = []

        response = self._call(
            f"associations/{from_object_type.value}/{to_object_type.value}/labels",
            method="GET",
        )
        results.extend([id_ for id_ in response["results"]])

        return results

    def create_schema(
        self,
        from_object_type: ObjectTypeDefinitions,
        to_object_type: ObjectTypeDefinitions,
        label: str,
        name: str,
        **options,
    ) -> Dict:
        """
        Create a user defined association label definition
        """

        response = self._call(
            f"associations/{from_object_type.value}/{to_object_type.value}/labels",
            method="POST",
            data={
                "label": label,
                "name": name,
            },
            **options,
        )
        if "results" in response and len(response) == 1:
            return response["results"][0]

        raise RuntimeError(
            f'Invalid response, results are not 1 item: {response["results"]}',
        )

    def update_schema(
        self,
        from_object_type: ObjectTypeDefinitions,
        to_object_type: ObjectTypeDefinitions,
        association_type_id: int,
        label: str,
        **options,
    ) -> None:
        """
        Update a user defined association label definition
        """
        return self._call(
            f"associations/{from_object_type.value}/{to_object_type.value}/labels",
            method="PUT",
            data={
                "label": label,
                "associationTypeId": association_type_id,
            },
            **options,
        )

    def delete_schema(
        self,
        from_object_type: ObjectTypeDefinitions,
        to_object_type: ObjectTypeDefinitions,
        association_type_id: int,
        **options,
    ) -> None:
        """
        Deletes an association label definition
        """
        return self._call(
            f"associations/{from_object_type.value}/{to_object_type.value}"
            f"/labels/{association_type_id}",
            method="DELETE",
            **options,
        )
