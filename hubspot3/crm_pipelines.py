"""
hubspot crm_pipelines api
"""
from hubspot3.base import BaseClient
from hubspot3.utils import get_log


CRM_PIPELINES_API_VERSION = "1"


class PipelinesClient(BaseClient):
    """
    The hubspot3 Pipelines client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        super(PipelinesClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.crm-pipelines")

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

    def get_deals_pipeline_by_id(self, pipeline_id: str):
        """
        Retrieve a deals pipeline by its id.

        Notes: At the moment, it is impossible to retrieve a pipeline by id directly through the
        hubspot API. We have to fetch all the pipelines of type 'DEAL' and then looks for a
        pipeline with the given `pipeline_id`.

        Returns
        -------
        dict
            The pipeline as returned by the Hubspot API.
            See the docstring of the `get_all_for_deals` method below to see an output example.

            None could be returned if no pipeline is matching with the given `pipeline_id`.
        """
        pipelines = self.get_all()
        for pipeline in pipelines:
            if pipeline.get("pipelineId") == pipeline_id:
                return pipeline
        return None
