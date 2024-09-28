# Copyright ©, 2024, Lightspark Group, Inc. - All Rights Reserved

import json
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import urlencode, urlparse, urlunparse
from uuid import uuid4

import aiohttp
import jwt
import pytest
import requests
from aioauth.utils import create_s256_code_challenge
from nostr_sdk import Keys
from quart import Response, current_app
from quart.app import QuartClient
from sqlalchemy.sql import select

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_currency
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.spending_limit import SpendingLimitFrequency
from nwc_backend.models.user import User
from nwc_backend.nostr.client_app_identity_lookup import ClientAppInfo


@pytest.mark.asyncio
async def test_create_client_app_connection_success(
    test_client: QuartClient,
) -> None:
    client_app_pubkey = Keys.generate().public_key()
    client_app_identity_relay = "wss://myrelay.info"
    client_id = f"{client_app_pubkey.to_hex()} {client_app_identity_relay}"
    required_commands = [
        Nip47RequestMethod.MAKE_INVOICE.value,
        Nip47RequestMethod.PAY_INVOICE.value,
    ]
    optional_commands = [
        Nip47RequestMethod.FETCH_QUOTE.value,
        Nip47RequestMethod.EXECUTE_QUOTE.value,
    ]
    code_verifier = token_hex()
    code_challenge = create_s256_code_challenge(code_verifier)
    redirect_uri = "www.pinkdrink.com"
    budget_amount = 100
    budget_currency = "USD"
    budget_frequency = SpendingLimitFrequency.WEEKLY
    request_params = {
        "client_id": client_id,
        "required_commands": " ".join(required_commands),
        "optional_commands": " ".join(optional_commands),
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
        "redirect_uri": redirect_uri,
        "budget": f"{budget_amount}.{budget_currency}/{budget_frequency.value}",
    }
    url_parts = list(urlparse("/oauth/auth"))
    query = urlencode(request_params)
    url_parts[4] = query

    # test first client app to oauth/auth call
    with patch(
        "nwc_backend.api_handlers.client_app_oauth_handler.look_up_client_app_identity",
        return_value=ClientAppInfo(
            pubkey=client_app_pubkey,
            identity_relay=client_app_identity_relay,
            allowed_redirect_urls=[redirect_uri],
        ),
    ), patch(
        "nwc_backend.api_handlers.client_app_oauth_handler.redirect",
        return_value=Response(status=200),
    ) as mock:
        await test_client.get(urlunparse(url_parts))
        mock.assert_called()

    async with test_client.app.app_context():
        client_app = await ClientApp.from_client_id(client_id)
        assert client_app
        assert client_app.nostr_pubkey == client_app_pubkey.to_hex()
        assert client_app.identity_relay == client_app_identity_relay

    # test second vasp to oauth/auth call
    user_vasp_id = str(uuid4())
    user_uma_address = "$alice@uma.com"
    async with test_client.app.app_context():
        token = jwt.encode(
            {
                "sub": user_vasp_id,
                "address": user_uma_address,
                "iss": "https://example.com",
                "aud": "https://example.com",
                "exp": int(
                    (datetime.now(timezone.utc) + timedelta(days=30)).timestamp()
                ),
            },
            current_app.config["UMA_VASP_JWT_PRIVKEY"],
            algorithm="ES256",
        )
    request_params["token"] = token
    url_parts = list(urlparse("/oauth/auth"))
    query = urlencode(request_params)
    url_parts[4] = query
    with patch(
        "nwc_backend.api_handlers.client_app_oauth_handler.redirect",
        return_value=Response(status=200),
    ) as mock:
        await test_client.get(urlunparse(url_parts))
        mock.assert_called()

    async with test_client.app.app_context():
        user = await User.from_vasp_user_id(user_vasp_id)
        assert user
        assert user.uma_address == user.uma_address

    # test third frontend /app/new call
    permissions = ["receive_payments", "send_payments"]
    request_data = {
        "permissions": permissions,
        "currencyCode": budget_currency,
        "amountInLowestDenom": budget_amount,
        "limitEnabled": True,
        "limitFrequency": budget_frequency.value,
        "expiration": "2025-01-01T00:00:00Z",
        "name": "Test Connection",
    }
    long_lived_token = token_hex()
    with patch.object(requests, "post") as mock_token_exchange_post, patch.object(
        aiohttp.ClientSession, "get"
    ) as mock_vasp_get_info:
        vasp_response = {"token": long_lived_token}
        mock_response = Mock()
        mock_response.json = Mock(return_value=vasp_response)
        mock_response.ok = True
        mock_token_exchange_post.return_value = mock_response

        vasp_response = {
            "pubkey": token_hex(),
            "network": "mainnet",
            "methods": [
                Nip47RequestMethod.FETCH_QUOTE.value,
                Nip47RequestMethod.EXECUTE_QUOTE.value,
            ],
            "currencies": [
                {
                    "currency": create_currency("USD").to_dict(),
                    "multiplier": 15351.4798,
                    "min": 1,
                    "max": 1000_00,
                }
            ],
        }
        mock_response = AsyncMock()
        mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
        mock_response.ok = True
        mock_vasp_get_info.return_value.__aenter__.return_value = mock_response

        response = await test_client.post("/apps/new", json=request_data)
        assert response.status_code == 200
        auth_code = json.loads((await response.data).decode())["code"]

    async with test_client.app.app_context():
        nwc_connection = await db.session.scalar(
            select(NWCConnection).filter_by(client_app_id=client_app.id)
        )
        assert nwc_connection
        assert nwc_connection.user_id == user.id
        assert nwc_connection.custom_name is None
        assert nwc_connection.granted_permissions_groups == permissions
        assert nwc_connection.long_lived_vasp_token == long_lived_token
        assert nwc_connection.redirect_uri == redirect_uri
        assert nwc_connection.code_challenge == code_challenge
        assert nwc_connection.authorization_code == auth_code
        assert nwc_connection.spending_limit.amount == budget_amount
        assert nwc_connection.spending_limit.frequency == budget_frequency

    # test fourth client api /oauth/token call
    request_data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    response = await test_client.post("/oauth/token", form=request_data)
    assert response.status_code == 200
    response_data = json.loads((await response.data).decode())
    nostr_keys = Keys.parse(response_data["access_token"])

    async with test_client.app.app_context():
        nwc_connection = await db.session.scalar(
            select(NWCConnection).filter_by(client_app_id=client_app.id)
        )
        assert nwc_connection
        assert nwc_connection.refresh_token == response_data["refresh_token"]
        assert nwc_connection.nostr_pubkey == nostr_keys.public_key().to_hex()
