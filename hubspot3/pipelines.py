from hubspot3.base import BaseClient
from hubspot3.utils import get_log


PIPELINES_API_VERSION = "1"


class PipelinesClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(PipelinesClient, self).__init__(*args, **kwargs)
        self.log = get_log("hubspot3.products")

    def _get_path(self, subpath: str):
        """
        Get the path of the crm-pipelines API.

        Parameters
        ---------
        subpath: str
        """
        return 'crm-pipelines/v{api_version}/pipelines/{subpath}'.format(
            api_version=PIPELINES_API_VERSION,
            subpath=subpath,
        )

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
        pipelines = self.get_all_for_deals()
        for pipeline in pipelines:
            if pipeline.get('pipelineId') == pipeline_id:
                return pipeline
        return None

    def get_all_for_deals(self):
        """
        Retrieve all the pipelines for objects of type `deals`.

        Cf: https://developers.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type

        Here is an example of a pipeline response:
        ```
        [{
            'pipelineId': '032da9ab-0544-4440-bee6-b02b8e15edb5',
            'createdAt': 1556114109315,
            'updatedAt': 1556114319558,
            'objectType': 'DEAL',
            'objectTypeId': '0-3',
            'label': 'TEST',
            'displayOrder': 1,
            'active': True,
            'stages': [
                {
                    'stageId': '63f9dc05-5bcb-4899-b9e4-504a2a04855d',
                    'createdAt': 0,
                    'updatedAt': 1556114319558,
                    'label': 'Deal accepted',
                    'displayOrder': 2,
                    'metadata': {'isClosed': 'true', 'probability': '1.0'},
                    'active': True
                }, {
                    'stageId': '455000',
                    'createdAt': 1556114109315,
                    'updatedAt': 1556114319558,
                    'label': 'Prospecting',
                    'displayOrder': 0,
                    'metadata': {'isClosed': 'false', 'probability': '0.1'},
                    'active': True
                }, {
                    'stageId': 'f5ca1a0f-2242-44b4-b858-e385f14ba842',
                    'createdAt': 0,
                    'updatedAt': 1556114319558,
                    'label': 'Deal refused',
                    'displayOrder': 3,
                    'metadata': {'isClosed': 'true', 'probability': '0.0'},
                    'active': True
                }, {
                    'stageId': 'e21953dd-cffb-4791-aa9b-1a178070514a',
                    'createdAt': 0,
                    'updatedAt': 1556114319558,
                    'label': 'Proposal sent',
                    'displayOrder': 1,
                    'metadata': {'isClosed': 'false', 'probability': '0.8'},
                    'active': True
                }
            ],
            'default': False
        }]
        ```

        Returns
        -------
        list of dict
        """
        response = self._call('deals', method='GET')
        try:
            return response['results']
        except KeyError:
            self.log.error(
                "Invalid 'crm-pipelines' response from the hubspot API.",
                extra={'response': response},
            )
            return []
