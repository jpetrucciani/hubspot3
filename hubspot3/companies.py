"""
hubspot companies api
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


COMPANIES_API_VERSION = '2'


class CompaniesClient(BaseClient):
    """
    The hubspot3 Companies client uses the _make_request method to call the API
    for data.  It returns a python object translated from the json return
    """

    def __init__(self, *args, **kwargs):
        super(CompaniesClient, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log('hapi.companies')

    def _get_path(self, subpath):
        return 'companies/v{}/{}'.format(
            self.options.get('version') or COMPANIES_API_VERSION,
            subpath
        )

    def create(self, data=None, **options):
        data = data or {}
        return self._call('companies/', data=data, method='POST', **options)

    def update(self, key, data=None, **options):
        data = data or {}
        return self._call(
            'companies/{}'.format(key),
            data=data,
            method='PUT',
            **options
        )

    def get(self, companyid, **options):
        return self._call('companies/{}'.format(companyid), method='GET', **options)

    def get_all(self, **options):
        finished = False
        output = []
        offset = 0
        querylimit = 250  # Max value according to docs
        while not finished:
            batch = self._call(
                'companies/paged', method='GET', doseq=True,
                params={
                    'limit': querylimit,
                    'offset': offset,
                    'properties': [
                        'name',
                        'description',
                        'address',
                        'address2',
                        'city',
                        'state',
                        'story',
                        'hubspot_owner_id'
                    ],
                },
                **options
            )
            output.extend([
                prettify(company, id_key='companyId')
                for company in batch['companies'] if not company['isDeleted']
            ])
            finished = not batch['has-more']
            offset = batch['offset']

        return output
