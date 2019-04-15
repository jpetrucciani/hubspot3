"""
hubspot crm_pipelines api
"""
from hubspot3 import logging_helper
from hubspot3.base import BaseClient


CRM_PIPELINES_API_VERSION = "1"


class PipelinesClient(BaseClient):
    """
    The hubspot3 Pipelines client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        super(PipelinesClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log("hubspot3.crm-pipelines")

    def _get_path(self, subpath):
        return "crm-pipelines/v{}/{}".format(
            self.options.get("version") or CRM_PIPELINES_API_VERSION, subpath
        )

    def create(self, object_type, data=None, **options):
        data = data or {}
        return self._call(
            "pipeline/{}".format(object_type), data=data, method="POST", **options
        )

    def update(self, object_type, key, data=None, **options):
        data = data or {}
        return self._call(
            "pipeline/{}/{}".format(object_type, key),
            data=data,
            method="PUT",
            **options
        )

    def get_all(self, object_type="deals", offset=0, extra_properties=None, **options):
        """
        get all crm_pipelines in the hubspot account with given object_type.
        object_type (default='deals'): must be 'deals' or 'tickets'
        extra_properties: a list used to extend the properties fetched
        """
        output = []

        output = self._call("pipelines/{}".format(object_type), method="GET", **options)

        return output["results"]
