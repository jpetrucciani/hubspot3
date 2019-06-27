from unittest.mock import Mock, patch
import pytest

from hubspot3 import ecommerce_bridge


@pytest.fixture
def ecommerce_bridge_client(mock_connection):
    client = ecommerce_bridge.EcommerceBridgeClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


@pytest.mark.parametrize(
    "object_type, num_messages, store_id, max_messages, expected_request_count",
    [
        ("CONTACT", 0, "default", 200, 0),
        ("CONTACT", 1, "default", 200, 1),
        ("CONTACT", 2, "my-store", 2, 1),
        ("CONTACT", 3, "default", 2, 2),
        ("CONTACT", 4, "another-store", 2, 2),
        ("PRODUCT", 5, "default", 2, 3),
        ("PRODUCT", 10, "my-store", 3, 4),
        ("PRODUCT", 10, "my-store", 200, 1),
    ],
)
def test_send_sync_messages(
    monkeypatch,
    ecommerce_bridge_client,
    mock_connection,
    object_type,
    num_messages,
    store_id,
    max_messages,
    expected_request_count,
):
    monkeypatch.setattr(
        ecommerce_bridge, "MAX_ECOMMERCE_BRIDGE_SYNC_MESSAGES", max_messages
    )
    mock_connection.set_response(204, "")

    # Prepare some dummy messages to send and split them up into the expected chunks.
    messages = [
        {
            "action": "UPSERT",
            "externalObjectId": str(i),
            "properties": {"email": "test{}@test.com".format(i)},
        }
        for i in range(1, num_messages + 1)
    ]
    expected_requests = [
        {
            "objectType": object_type,
            "storeId": store_id,
            "messages": messages[i:i + max_messages],
        }
        for i in range(0, num_messages, max_messages)
    ]

    assert (
        ecommerce_bridge_client.send_sync_messages(object_type, messages, store_id)
        is None
    )
    mock_connection.assert_num_requests(expected_request_count)
    for data in expected_requests:
        mock_connection.assert_has_request(
            "PUT", "/extensions/ecomm/v2/sync/messages?", data
        )


@pytest.mark.parametrize(
    "subpath, include_resolved, error_type, object_type, limit, num_errors, max_errors, "
    "expected_pages",
    [
        ("sync/errors/portal", False, None, None, None, 10, 200, [1]),
        ("sync/errors/portal", True, None, None, 10, 10, 200, [1]),
        ("sync/errors/portal", True, None, None, 5, 10, 200, [1]),
        ("sync/errors/app/1337", True, None, None, 10, 10, 5, [1, 6]),
        ("sync/errors/app/1337", False, "CONTACT", None, None, 42, 20, [1, 21, 41]),
        ("sync/errors/app/1337", True, None, "SETTINGS_NOT_ENABLED", 10, 5, 200, [1]),
    ],
)
def test_get_sync_errors(
    monkeypatch,
    ecommerce_bridge_client,
    mock_connection,
    subpath,
    include_resolved,
    error_type,
    object_type,
    limit,
    num_errors,
    max_errors,
    expected_pages,
):
    monkeypatch.setattr(
        ecommerce_bridge, "MAX_ECOMMERCE_BRIDGE_SYNC_ERRORS", max_errors
    )

    # Prepare some dummy errors for the response and split them up into the expected chunks.
    errors = [
        {
            "portalId": 12345,
            "storeId": "default",
            "objectType": object_type or "CONTACT",
            "externalObjectId": str(i),
            "changedAt": 1507642200000 + i,
            "erroredAt": 1525730425475 + i,
            "type": error_type or "MISSING_REQUIRED_PROPERTY",
            "details": "An error occurred.",
            "status": "OPEN",
        }
        for i in range(num_errors)
    ]
    # Always return as many results as possible even if a limit was set to test that the return
    # value will still be limited, even if more results than expected were received.
    responses = [
        {"results": errors[i:i + max_errors]}
        for i in range(0, num_errors, max_errors)
    ]
    for i, response in enumerate(responses[:-1], start=2):
        response["paging"] = {"next": {"page": str(i), "link": "dummy"}}
    mock_connection.set_responses([(200, response) for response in responses])

    # Check that the correct number of requests was performed and that the results match the
    # expectation.
    result = ecommerce_bridge_client._get_sync_errors(
        subpath, include_resolved, error_type, object_type, limit
    )
    assert len(result) == min(limit or num_errors, num_errors)
    assert result == errors[:limit]
    mock_connection.assert_num_requests(len(expected_pages))

    # Check that all requests were performed with the correct parameters.
    common_params = {
        "includeResolved": str(include_resolved).lower(),
        "limit": min(limit or max_errors, max_errors),
    }
    if error_type:
        common_params["errorType"] = error_type
    if object_type:
        common_params["objectType"] = object_type
    for page in expected_pages:
        mock_connection.assert_query_parameters_in_request(
            **dict(common_params, page=page)
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(),
        dict(limit=10),
        dict(include_resolved=True, object_type="CONTACT"),
        dict(
            include_resolved=True,
            object_type="CONTACT",
            error_type="MISSING_REQUIRED_PROPERTY",
            timeout=30,
        ),
    ],
)
def test_get_sync_errors_for_account(ecommerce_bridge_client, kwargs):
    with patch.object(
        ecommerce_bridge_client, "_get_sync_errors"
    ) as mock_get_sync_errors:
        ecommerce_bridge_client.get_sync_errors_for_account(**kwargs)
        kwargs.setdefault("include_resolved", False)
        kwargs.setdefault("error_type", None)
        kwargs.setdefault("object_type", None)
        kwargs.setdefault("limit", None)
        mock_get_sync_errors.assert_called_once_with("sync/errors/portal", **kwargs)


@pytest.mark.parametrize(
    "app_id, kwargs",
    [
        (1337, dict()),
        (42, dict(limit=10)),
        (1337, dict(include_resolved=True, object_type="CONTACT")),
        (
            42,
            dict(
                include_resolved=True,
                object_type="CONTACT",
                error_type="MISSING_REQUIRED_PROPERTY",
                timeout=30,
            ),
        ),
    ],
)
def test_get_sync_errors_for_app(ecommerce_bridge_client, app_id, kwargs):
    with patch.object(
        ecommerce_bridge_client, "_get_sync_errors"
    ) as mock_get_sync_errors:
        ecommerce_bridge_client.get_sync_errors_for_app(app_id, **kwargs)
        kwargs.setdefault("include_resolved", False)
        kwargs.setdefault("error_type", None)
        kwargs.setdefault("object_type", None)
        kwargs.setdefault("limit", None)
        mock_get_sync_errors.assert_called_once_with(
            "sync/errors/app/{}".format(app_id), **kwargs
        )
