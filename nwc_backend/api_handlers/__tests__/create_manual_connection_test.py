# Copyright ©, 2024, Lightspark Group, Inc. - All Rights Reserved
import json
from unittest.mock import Mock, patch
import requests
from nwc_backend.db import db
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import PermissionsGroup

from secrets import token_hex
from uuid import uuid4

import pytest
from quart.app import QuartClient

from nwc_backend.models.__tests__.model_examples import (
    create_client_app,
    create_user,
    jwt_for_user,
)
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import PermissionsGroup


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
        "customName": "Test Connection",
    }

    response = await test_client.post("/api/connection/manual", json=request_data)
    assert response.status_code == 200
    response_json = json.loads(response.data)
    assert response_json["connectionId"] is not None
    assert response_json["pairingUri"] is not None