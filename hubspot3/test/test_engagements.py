"""Testing hubspot3.engagements 

This file tests the methods in the hubspot3.engagements file
"""
import json
from unittest.mock import Mock

from hubspot3 import engagements

import pytest


@pytest.fixture
def engagements_client(mock_connection):
    client = engagements.EngagementsClient(disable_auth=True)
    client.options["connection_type"] = Mock(return_value=mock_connection)
    return client


class TestEngagementsClient(object):
    def test_get_path(self):
        client = engagements.EngagementsClient(disable_auth=True)
        subpath = "engagements"
        assert client._get_path(subpath) == "engagements/v1/engagements"

    @pytest.mark.parametrize("start_date, end_date", [(500, 2000)],)
        self,
        engagements_client,
        mock_connection,
        start_date,
        end_date,
    ):

        params = {"since": start_date}

        response_body = {
            "results": [
                {
                    "engagement": {
                        "id": 420584370,
                        "portalId": 62515,
                        "active": True,
                        "createdAt": 1635476499000,
                        "lastUpdated": 1000,
                        "createdBy": 12345,
                        "modifiedBy": 12345,
                        "type": "CALL",
                        "timestamp": 1635476499000
                    },
                    "metadata": {
                        "body": "This was a call",
                        "disposition": "17b47fee-58de-441e-a44c-c6300d46f273"
                    }
                },
                {
                    "engagement": {
                        "id": 420569029,
                        "portalId": 62515,
                        "active": True,
                        "createdAt": 1535476299000,
                        "lastUpdated": 100,
                        "createdBy": 12345,
                        "modifiedBy": 12345,
                        "type": "NOTE",
                        "timestamp": 1535476299000
                    },
                    "metadata": {
                        "body": "This is a note"
                    }
                }
            ],
            "hasMore": False,
            "offset": 0
        }

        mock_connection.set_response(200, json.dumps(response_body))
        resp = list(engagements_client.get_recently_modified(start_date, end_date))

        mock_connection.assert_num_requests(1)
        mock_connection.assert_has_request(
            "GET", "/engagements/v1/engagements/recent/modified", **params
        )

        assert len(resp) == 1
        assert "id" in resp[0]["engagement"]
        assert 420584370 == resp[0]["engagement"]["id"]
