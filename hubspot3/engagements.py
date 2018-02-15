"""
hubspot engagements api
"""
from hubspot3 import (
    logging_helper
)
from hubspot3.base import (
    BaseClient
)


ENGAGEMENTS_API_VERSION = '1'


class EngagementsClient(BaseClient):
    """
    The hubspot3 Engagements client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json return
    """
    def __init__(self, *args, **kwargs):
        super(EngagementsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log('hapi.engagements')

    def _get_path(self, subpath):
        return 'engagements/v{}/{}'.format(
            self.options.get('version') or ENGAGEMENTS_API_VERSION,
            subpath
        )

    def get(self, engagement_id, **options):
        """Get a HubSpot engagement."""
        return self._call('engagements/{}'.format(engagement_id), method='GET', **options)

    def get_associated(self, object_type, object_id, **options):
        """Get associated HubSpot engagements."""
        return self._call('engagements/associated/{}/{}/paged'
                          .format(object_type, object_id), method='GET', **options)

    def create(self, data=None, **options):
        data = data or {}
        return self._call('engagements', data=data, method='POST', **options)

    def update(self, key, data=None, **options):
        data = data or {}
        return self._call('engagements/{}'.format(key), data=data,
                          method='PUT', **options)

    def get_all(self, **options):
        finished = False
        output = []
        querylimit = 250  # Max value according to docs
        offset = 0
        while not finished:
            batch = self._call(
                'engagements/paged', method='GET',
                params={'limit': querylimit, 'offset': offset}, **options
            )
            output.extend(batch['results'])
            finished = not batch['hasMore']
            offset = batch['offset']

        return output
