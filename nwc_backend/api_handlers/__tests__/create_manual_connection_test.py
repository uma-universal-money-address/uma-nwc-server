# Copyright ©, 2024, Lightspark Group, Inc. - All Rights Reserved

from secrets import token_hex
from unittest.mock import Mock, patch
from urllib.parse import urlparse

import pytest
import requests
from quart.app import QuartClient

from nwc_backend.models.__tests__.model_examples import create_user, jwt_for_user


@pytest.mark.asyncio
@patch.object(requests, "post")
async def test_create_manual_connection_success(
    mock_post: Mock,
    test_client: QuartClient,
) -> None:
    vasp_response = {
        "token": token_hex(),
    }
    mock_response = Mock()
    mock_response.json = Mock(return_value=vasp_response)
    mock_response.ok = True
    mock_post.return_value = mock_response

    async with test_client.app.app_context():
        user = await create_user()
    async with test_client.session_transaction() as session:
        session["user_id"] = user.id
        session["short_lived_vasp_token"] = jwt_for_user(user)

    request_data = {
        "permissions": ["receive_payments", "send_payments"],
        "currencyCode": "USD",
        "amountInLowestDenom": 1000,
        "limitEnabled": True,
        "limitFrequency": "monthly",
        "expiration": "2025-01-01T00:00:00Z",
        "name": "Test Connection",
    }

    response = await test_client.post("/api/connection/manual", json=request_data)
    assert response.status_code == 200
    response_json = await response.get_json()
    assert response_json["connectionId"] is not None
    pairing_uri = response_json["pairingUri"]
    assert pairing_uri is not None
    parsed_uri = urlparse(pairing_uri)
    query_params = dict([pair.split("=") for pair in parsed_uri.query.split("&")])
    assert query_params["secret"] is not None
    assert query_params["lud16"] == user.uma_address
