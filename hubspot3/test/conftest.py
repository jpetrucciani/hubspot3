"""
configure pytest
"""
import json
from http.client import HTTPSConnection
from unittest.mock import MagicMock, Mock
from urllib.parse import urlencode

import pytest


@pytest.fixture
def mock_connection():
    """
    A mock connection object that can be used in place of HTTP(S)Connection objects to avoid to
    actually perform requests. Offers some utilities to check if certain requests were performed.
    """
    connection = Mock(spec=HTTPSConnection, host="api.hubapi.com", timeout=10)

    def assert_num_requests(number):
        """Assert that a certain number of requests was made."""
        assert connection.request.call_count == number

    connection.assert_num_requests = assert_num_requests

    def assert_has_request(method, url, data=None, **params):
        """
        Assert that at least one request with the exact combination of method, URL, body data, and
        query parameters was performed.
        """
        for args, kwargs in connection.request.call_args_list:
            request_method = args[0]
            request_url = args[1]
            request_data = args[2]

            if data is not None and not isinstance(data, str):
                request_data = json.loads(request_data)

            url_check = (
                request_url == url if not params else request_url.startswith(url)
            )
            params_check = all(
                urlencode({name: value}, doseq=True) in request_url
                for name, value in params.items()
            )
            if (
                request_method == method
                and url_check
                and request_data == data
                and params_check
            ):
                break
        else:
            raise AssertionError(
                (
                    "No {method} request to URL '{url}' with data '{data}' and with parameters "
                    "'{params}' was performed.'"
                ).format(method=method, url=url, data=data, params=params)
            )

    connection.assert_has_request = assert_has_request

    def set_response(status_code, body):
        """Set the response status code and body for all mocked requests."""
        response = MagicMock(status=status_code)
        response.read.return_value = body
        connection.getresponse.return_value = response

    connection.set_response = set_response

    def set_responses(response_tuples):
        """
        Set multiple responses for consecutive mocked requests via tuples of (status code, body).
        The first request will result in the first response, the second request in the
        second response and so on.
        """
        responses = []
        for status_code, body in response_tuples:
            response = MagicMock(status=status_code)
            response.read.return_value = body
            responses.append(response)
        connection.getresponse.side_effect = responses

    connection.set_responses = set_responses

    connection.set_response(200, "")
    return connection
