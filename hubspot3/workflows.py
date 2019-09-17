"""
hubspot workflows api
"""
from hubspot3.base import BaseClient
from hubspot3.utils import get_log

WORKFLOWS_API_VERSION = "3"

class WorkflowsClient(BaseClient):
    """
    The hubspot3 Workflows client uses the _make_request method to call the
    API for data.  It returns a python object translated from the json returned
    """

    def __init__(self, *args, **kwargs):
        """initialize a workflows client"""
        super(WorkflowsClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.workflows")

    def _get_path(self, subpath):
        return "automation/v{}/{}".format(WORKFLOWS_API_VERSION, subpath)

    def get_all_workflow_ids(self, **options):
        """
        Get all workflow IDs
        :see: https://developers.hubspot.com/docs/methods/workflows/v3/get_workflows
        """
        return self._call("workflows", **options)

    def get_workflow_by_id(self, workflow_id: int = None, **options):
        """
        Get workflow specified by ID
        :see: https://developers.hubspot.com/docs/methods/workflows/v3/get_workflow
        """
        if workflow_id is not None:
            return self._call("workflows/{}".format(workflow_id))
