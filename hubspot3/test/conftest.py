"""
configure pytest
"""
from http.client import HTTPSConnection
import json
from urllib.parse import urlencode

from unittest.mock import MagicMock, Mock
import pytest


@pytest.fixture
def mock_connection():
    """
    A mock connection object that can be used in place of HTTP(S)Connection objects to avoid to
    actually perform requests. Offers some utilities to check if certain requests were performed.
    """
    connection = Mock(spec=HTTPSConnection, host="api.hubapi.com", timeout=10)

    def assert_num_requests(number):
        """Assert that a certain number of requests were made."""
        assert connection.request.call_count == number

    connection.assert_num_requests = assert_num_requests

    def assert_has_request(method, url, data=None):
        """
        Assert that at least one request with the exact combination of method, URL and body data
        was performed.
        """
        data = json.dumps(data) if data else None
        for args, kwargs in connection.request.call_args_list:
            if args[0] == method and args[1] == url and args[2] == data:
                break
        else:
            raise AssertionError(
                "No {method} request to URL '{url}' with data '{data}' was performed.'".format(
                    method=method, url=url, data=data
                )
            )

    connection.assert_has_request = assert_has_request

    def assert_query_parameters_in_request(**params):
        """
        Assert that at least one request using all of the given query parameters was performed.
        """
        for args, kwargs in connection.request.call_args_list:
            url = args[1]
            if all(
                urlencode({name: value}, doseq=True) in url
                for name, value in params.items()
            ):
                break
        else:
            raise AssertionError(
                "No request contains all given query parameters: {}".format(params)
            )

    connection.assert_query_parameters_in_request = assert_query_parameters_in_request

    def set_response(status_code, body):
        """Set the response status code and body for all mocked requests."""
        response = MagicMock(status=status_code)
        response.read.return_value = body
        connection.getresponse.return_value = response

    connection.set_response = set_response

    def set_responses(response_tuples):
        """
        Set multiple responses for consecutive mocked requests via tuples of (status code, body).
        The first request will result will result in the first response, the second request in the
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
