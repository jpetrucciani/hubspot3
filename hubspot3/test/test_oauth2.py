import json
from urllib.parse import urlencode

from unittest.mock import Mock, patch
import pytest

from hubspot3.oauth2 import OAuth2Client


@pytest.fixture
def mock_urlencode():
    """
    A mocked `urlencode` function that still calls the original function, but additionally stores
    the last result in the `last_return_value` attribute.
    """
    mock = Mock()

    def wrapper(*args, **kwargs):
        mock.last_return_value = urlencode(*args, **kwargs)
        return mock.last_return_value

    mock.side_effect = wrapper
    with patch("hubspot3.oauth2.urlencode", mock):
        yield mock


@pytest.mark.parametrize(
    "access_token, api_key, disable_auth",
    [
        (None, None, False),
        ("abc123", None, False),
        (None, "def456", False),
        ("abc123", "def456", False),
        (None, None, True),
        ("abc123", None, True),
        (None, "def456", True),
        ("abc123", "def456", True),
    ],
)
def test_initializer(access_token, api_key, disable_auth):
    client = OAuth2Client(
        access_token=access_token, api_key=api_key, disable_auth=disable_auth
    )
    assert client.access_token is None
    assert client.api_key is None
    assert client.options["disable_auth"] is True


@pytest.mark.parametrize(
    "init_kwargs, call_kwargs, expected_data, expected_refresh_token",
    [
        (
            dict(),
            dict(
                authorization_code="code123",
                redirect_uri="redirect.com",
                client_id="id123",
                client_secret="secret123",
            ),
            [
                "code=code123",
                "redirect_uri=redirect.com",
                "client_id=id123",
                "client_secret=secret123",
                "grant_type=authorization_code",
            ],
            None,
        ),
        (
            dict(client_id="id123"),
            dict(
                authorization_code="code123", redirect_uri="redirect.com", client_secret="secret123"
            ),
            [
                "code=code123",
                "redirect_uri=redirect.com",
                "client_id=id123",
                "client_secret=secret123",
                "grant_type=authorization_code",
            ],
            None,
        ),
        (
            dict(client_id="id456", refresh_token="token456"),
            dict(
                authorization_code="code123", redirect_uri="redirect.com", client_secret="secret456"
            ),
            [
                "code=code123",
                "redirect_uri=redirect.com",
                "client_id=id456",
                "client_secret=secret456",
                "grant_type=authorization_code",
            ],
            "token456",
        ),
        (
            dict(
                client_id="id456", client_secret="secret456", refresh_token="token456"
            ),
            dict(authorization_code="code123", redirect_uri="redirect.com"),
            [
                "code=code123",
                "redirect_uri=redirect.com",
                "client_id=id456",
                "client_secret=secret456",
                "grant_type=authorization_code",
            ],
            "rt123",
        ),
    ],
)
def test_get_tokens(
    mock_connection,
    mock_urlencode,
    init_kwargs,
    call_kwargs,
    expected_data,
    expected_refresh_token,
):
    client = OAuth2Client(**init_kwargs)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    mock_connection.set_response(
        200,
        json.dumps(
            {"access_token": "at123", "refresh_token": "rt123", "expires_in": 21600}
        ),
    )

    client.get_tokens(**call_kwargs)
    data = mock_urlencode.last_return_value
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request("POST", "/oauth/v1/token?", data)
    assert all(part in data for part in expected_data)
    assert client.refresh_token == expected_refresh_token


@pytest.mark.parametrize(
    "init_kwargs, call_kwargs, expected_data, expected_refresh_token",
    [
        (
            dict(),
            dict(
                client_id="id123", client_secret="secret123", refresh_token="token123"
            ),
            [
                "client_id=id123",
                "client_secret=secret123",
                "refresh_token=token123",
                "grant_type=refresh_token",
            ],
            None,
        ),
        (
            dict(client_id="id123"),
            dict(client_secret="secret123", refresh_token="token123"),
            [
                "client_id=id123",
                "client_secret=secret123",
                "refresh_token=token123",
                "grant_type=refresh_token",
            ],
            None,
        ),
        (
            dict(client_id="id456", refresh_token="token456"),
            dict(client_secret="secret456"),
            [
                "client_id=id456",
                "client_secret=secret456",
                "refresh_token=token456",
                "grant_type=refresh_token",
            ],
            "token456",
        ),
        (
            dict(
                client_id="id456", client_secret="secret456", refresh_token="token456"
            ),
            dict(),
            [
                "client_id=id456",
                "client_secret=secret456",
                "refresh_token=token456",
                "grant_type=refresh_token",
            ],
            "rt123",
        ),
    ],
)
def test_refresh_tokens(
    mock_connection,
    mock_urlencode,
    init_kwargs,
    call_kwargs,
    expected_data,
    expected_refresh_token,
):
    client = OAuth2Client(**init_kwargs)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    mock_connection.set_response(
        200,
        json.dumps(
            {"access_token": "at123", "refresh_token": "rt123", "expires_in": 21600}
        ),
    )

    client.refresh_tokens(**call_kwargs)
    data = mock_urlencode.last_return_value
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request("POST", "/oauth/v1/token?", data)
    assert all(part in data for part in expected_data)
    assert client.refresh_token == expected_refresh_token
