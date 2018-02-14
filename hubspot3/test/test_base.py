import unittest
import json
import zlib
from collections import (
    defaultdict
)
from hubspot3.base import (
    BaseClient
)
from hubspot3.error import (
    HubspotError
)


class TestBaseClient(BaseClient):
    def _get_path(self, subpath):
        return 'unit_path/{}'.format(subpath)


class TestResult(object):
    def __init__(self, *args, **kwargs):
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

    def getheaders(self):
        return []


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.client = TestBaseClient('unit_api_key')

    def tearDown(self):
        pass

    def test_prepare_request(self):
        subpath = 'unit_sub_path'
        params = {'duplicate': ['key', 'value']}
        data = None
        opts = {}
        doseq = False

        # with doseq=False we should encode the array
        # so duplicate=[key,value]
        url, headers, data = self.client._prepare_request(subpath, params, data, opts, doseq)
        self.assertTrue('duplicate=%5B%27key%27%2C+%27value%27%5D' in url)

        # with doseq=True the values will be split and assigned their own key
        # so duplicate=key&duplicate=value
        doseq = True
        url, headers, data = self.client._prepare_request(subpath, params, data, opts, doseq)
        print(url)
        self.assertTrue('duplicate=key&duplicate=' in url)

    def test_call(self):
        client = TestBaseClient('key', api_base='base', env='hudson')
        client.sleep_multiplier = .02
        client._create_request = lambda *args: None

        counter = dict(count=0)
        args = ('/my-api-path', {'bebop': 'rocksteady'})
        kwargs = dict(method='GET', data={}, doseq=False, number_retries=3)

        def execute_request_with_retries(a, b):
            counter['count'] += 1
            if counter['count'] < 2:
                raise HubspotError(defaultdict(str), defaultdict(str))
            else:
                return TestResult(body='SUCCESS')
        client._execute_request_raw = execute_request_with_retries

        # This should fail once, and then succeed
        result = client._call(*args, **kwargs)
        self.assertEqual(2, counter['count'])
        self.assertEqual('SUCCESS', result)

        def execute_request_failed(a, b):
            raise HubspotError(defaultdict(str), defaultdict(str))

        # This should fail and retry and still fail
        client._execute_request_raw = execute_request_failed
        raised_error = False
        try:
            client._call(*args, **kwargs)
        except HubspotError:
            raised_error = True
        self.assertTrue(raised_error)

    def test_digest_result(self):
        """
        Test parsing returned data in various forms
        """
        plain_text = 'Hello Plain Text'
        data = self.client._process_body(plain_text, False)
        self.assertEqual(plain_text, data)

        raw_json = '{"hello": "json"}'
        data = json.loads(self.client._process_body(raw_json, False))
        # Should parse as json into dict
        self.assertEqual(data.get('hello'), 'json')

        payload = zlib.compress('{"hello": "gzipped"}'.encode())

        data = json.loads(self.client._process_body(payload, True))
        self.assertEqual(data.get('hello'), 'gzipped')
