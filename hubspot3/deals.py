"""
hubspot deals api
"""
from hubspot3 import (
    logging_helper
)
from hubspot3.base import (
    BaseClient
)
from hubspot3.utils import (
    prettify
)

import urllib.parse

DEALS_API_VERSION = '1'


class DealsClient(BaseClient):
    """
    The hubspot3 Deals client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json return
    """
    def __init__(self, *args, **kwargs):
        super(DealsClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log('hapi.deals')

    def _get_path(self, subpath):
        return 'deals/v{}/{}'.format(
            self.options.get('version') or DEALS_API_VERSION,
            subpath
        )

    def get(self, deal_id, **options):
        return self._call('deal/{}'.format(deal_id), method='GET', **options)

    def create(self, data=None, **options):
        data = data or {}
        return self._call('deal/', data=data, method='POST', **options)

    def update(self, key, data=None, **options):
        data = data or {}
        return self._call('deal/{}'.format(key), data=data,
                          method='PUT', **options)

    def associate(self, deal_id, object_type, object_ids, **options):
        # Encoding the query string here since HubSpot is expecting the "id" parameter to be
        # repeated for each object ID, which is not a standard practice and won't work otherwise.
        object_ids = [('id', object_id) for object_id in object_ids]
        query = urllib.parse.urlencode(object_ids)

        return self._call(
            'deal/{}/associations/{}'.format(deal_id, object_type),
            method='PUT',
            query=query,
            **options
        )

    def get_all(self, limit=None, offset=0, **options):
        finished = False
        output = []
        offset = 0
        querylimit = 250  # Max value according to docs
        while not finished:
            batch = self._call(
                'deal/paged',
                method='GET',
                params={
                    'limit': querylimit,
                    'offset': offset,
                    'properties': [
                        'associations',
                        'dealname',
                        'dealstage',
                        'pipeline',
                        'hubspot_owner_id',
                        'description',
                        'closedate',
                        'amount',
                        'dealtype',
                        'createdate'
                    ],
                    'includeAssociations': True
                },
                doseq=True,
                **options
            )
            output.extend([
                prettify(deal, id_key='dealId')
                for deal in batch['deals'] if not deal['isDeleted']
            ])
            finished = not batch['hasMore']
            offset = batch['offset']

        return output
