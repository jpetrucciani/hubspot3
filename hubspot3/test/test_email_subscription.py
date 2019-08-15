import json

from unittest.mock import Mock
import pytest

from hubspot3.email_subscription import EmailSubscriptionClient


@pytest.fixture
def email_subscription_client(mock_connection):
    client = EmailSubscriptionClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


@pytest.mark.parametrize("portal_id", [None, 62515])
def test_get_status(email_subscription_client, mock_connection, portal_id):
    dummy_response = {
        "subscribed": False,
        "markedAsSpam": False,
        "portalId": 62515,
        "bounced": False,
        "email": "jerry@example.org",
        "subscriptionStatuses": [],
        "status": "unsubscribed",
    }
    mock_connection.set_response(200, json.dumps(dummy_response))
    expected_params = {}
    if portal_id:
        expected_params["portalId"] = portal_id

    result = email_subscription_client.get_status("jerry@example.org", portal_id)
    assert result == dummy_response
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request(
        "GET", "/email/public/v1/subscriptions/jerry@example.org?", **expected_params
    )


def test_update_status(email_subscription_client, mock_connection):
    data = {
        "subscriptionStatuses": [
            {
                "id": 7,
                "subscribed": True,
                "optState": email_subscription_client.OptState.OPT_IN,
                "legalBasis": email_subscription_client.LegalBasis.PERFORMANCE_OF_CONTRACT,
                "legalBasisExplanation": "We need to send them these emails as part of our agreement with them.",
            }
        ],
        "portalSubscriptionLegalBasis": email_subscription_client.LegalBasis.LEGITIMATE_INTEREST_CLIENT,
        "portalSubscriptionLegalBasisExplanation": "They told us at a conference that they're "
        "interested in receiving communications.",
    }
    assert email_subscription_client.update_status("jerry@example.org", data) is None
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request(
        "PUT", "/email/public/v1/subscriptions/jerry@example.org?", data
    )


@pytest.mark.parametrize(
    "legal_basis, explanation",
    [
        (None, None),
        (EmailSubscriptionClient.LegalBasis.LEGITIMATE_INTEREST_CLIENT, None),
        (
            None,
            "They told us at a conference that they're interested in receiving communications.",
        ),
        (
            EmailSubscriptionClient.LegalBasis.LEGITIMATE_INTEREST_CLIENT,
            "They told us at a conference that they're interested in receiving communications.",
        ),
    ],
)
def test_update_subscriptions(
    email_subscription_client, mock_connection, legal_basis, explanation
):
    subscriptions = [
        {
            "id": 7,
            "subscribed": True,
            "optState": email_subscription_client.OptState.OPT_IN,
            "legalBasis": email_subscription_client.LegalBasis.PERFORMANCE_OF_CONTRACT,
            "legalBasisExplanation": "We need to send them these emails as part of our agreement with them.",
        },
        {
            "id": 8,
            "subscribed": True,
            "optState": email_subscription_client.OptState.OPT_IN,
            "legalBasis": email_subscription_client.LegalBasis.PERFORMANCE_OF_CONTRACT,
            "legalBasisExplanation": "We need to send them these emails as part of our agreement with them.",
        },
    ]
    expected_data = {"subscriptionStatuses": subscriptions}
    if legal_basis:
        expected_data["portalSubscriptionLegalBasis"] = legal_basis
    if explanation:
        expected_data["portalSubscriptionLegalBasisExplanation"] = explanation

    email_subscription_client.update_subscriptions(
        "jerry@example.org", subscriptions, legal_basis, explanation
    )
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request(
        "PUT", "/email/public/v1/subscriptions/jerry@example.org?", expected_data
    )


def test_unsubscribe_permanently(email_subscription_client, mock_connection):
    assert (
        email_subscription_client.unsubscribe_permanently("jerry@example.org") is None
    )
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request(
        "PUT",
        "/email/public/v1/subscriptions/jerry@example.org?",
        {"unsubscribeFromAll": True},
    )


@pytest.mark.parametrize("portal_id", [None, 445715])
def test_get_topics(email_subscription_client, mock_connection, portal_id):
    dummy_response = {
        "subscriptionDefinitions": [
            {
                "active": True,
                "portalId": 12345,
                "description": "The default unsubscribe list that all emails in your hub will use",
                "id": 7,
                "name": "Default",
            },
            {
                "active": True,
                "portalId": 12345,
                "description": "Our weekly newsletter informing you about our new happenings",
                "id": 146,
                "name": "Weekly Newsletter",
            },
        ]
    }
    mock_connection.set_response(200, json.dumps(dummy_response))
    expected_params = {}
    if portal_id:
        expected_params["portalId"] = portal_id

    result = email_subscription_client.get_subscription_types(portal_id)
    assert result == dummy_response
    mock_connection.assert_num_requests(1)
    mock_connection.assert_has_request(
        "GET", "/email/public/v1/subscriptions/?", **expected_params
    )
