# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from dataclasses import dataclass
from secrets import token_hex
from typing import Any, Optional
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
from nostr_sdk import (
    ErrorCode,
    Event,
    EventId,
    Keys,
    Kind,
    KindEnum,
    Output,
    SendEventOutput,
    nip04_decrypt,
)
from quart.app import QuartClient
from sqlalchemy.sql import select
from uma_auth.models.error_response import ErrorCode as VaspErrorCode
from uma_auth.models.error_response import ErrorResponse as VaspErrorResponse

from nwc_backend.db import db
from nwc_backend.event_handlers.event_builder import EventBuilder
from nwc_backend.event_handlers.nip47_event_handler import handle_nip47_event
from nwc_backend.models.__tests__.model_examples import (
    create_app_connection,
    create_nip47_request,
)
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.permissions_grouping import PermissionsGroup
from nwc_backend.nostr_config import NostrConfig


@dataclass
class Harness:
    client_app_keys: Keys
    nwc_keys: Keys

    @classmethod
    def prepare(cls) -> "Harness":
        client_app_keys = Keys.generate()
        nwc_keys = NostrConfig.instance().identity_keys
        return Harness(client_app_keys=client_app_keys, nwc_keys=nwc_keys)

    def create_request_event(
        self,
        method: Nip47RequestMethod = Nip47RequestMethod.PAY_INVOICE,
        params: Optional[dict[str, Any]] = None,
    ) -> Event:
        if params is None:
            params = self.get_default_request_params()
        return (
            EventBuilder(
                kind=KindEnum.WALLET_CONNECT_REQUEST(),  # pyre-ignore[6]
                content=json.dumps(
                    {
                        "method": method.value,
                        "params": params,
                    }
                ),
                keys=self.client_app_keys,
            )
            .encrypt_content(self.nwc_keys.public_key())
            .add_tag(["p", self.nwc_keys.public_key().to_hex()])
            .build()
        )

    def get_default_request_params(self) -> dict[str, Any]:
        return {
            "invoice": "lnbcrt1u1pjd4dnypp556q6aag8hf6rweejfdv8tp2v4034jdfvxj8p94rr2fwgvuy8xxxqsp5cqyc3alzjf3ua6up2jpvfu9xqa8rjk5txpeh3jhvcm2h8xprk8kqxqyz5vqnp4qga909cwg8hfr95yqftg6k7a99cm5f8xpzuven6680l0vancdhyjvcqzpgdqq9qyyssq2tcyjf6l4at69ljxnk8wcnx20s3qn2k356pn86qjah83ym3dhg4n48ukdmw79axgtd4fj6e9cezjyyca7m28q2flcj2wua0an5434dgppwa0mv"
        }

    def _load_encrypted_content(self, encrypted_content: str) -> dict[str, Any]:
        content = nip04_decrypt(
            secret_key=self.nwc_keys.secret_key(),
            public_key=self.client_app_keys.public_key(),
            encrypted_content=encrypted_content,
        )
        return json.loads(content)

    def validate_response_event(
        self, response_event: Any, request_event_id: EventId  # pyre-ignore[2]
    ) -> dict[str, Any]:
        assert isinstance(response_event, Event)
        assert response_event.verify()
        assert response_event.author() == self.nwc_keys.public_key()
        assert response_event.kind() == Kind.from_enum(
            KindEnum.WALLET_CONNECT_RESPONSE()  # pyre-ignore[6]
        )
        assert response_event.event_ids() == [request_event_id]
        return self._load_encrypted_content(response_event.content())


@patch("nwc_backend.nostr_client.nostr_client.send_event", new_callable=AsyncMock)
async def test_failed__no_app_connection(
    mock_nostr_send: AsyncMock,
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        harness = Harness.prepare()
        request_event = harness.create_request_event()
        await handle_nip47_event(request_event)

        mock_nostr_send.assert_called_once()
        response_event = mock_nostr_send.call_args[0][0]
        content = harness.validate_response_event(response_event, request_event.id())
        assert content["error"]["code"] == ErrorCode.UNAUTHORIZED.name


@patch("nwc_backend.nostr_client.nostr_client.send_event", new_callable=AsyncMock)
async def test_failed__access_token_expired(
    mock_nostr_send: AsyncMock,
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        harness = Harness.prepare()
        await create_app_connection(
            keys=harness.client_app_keys,
            granted_permissions_groups=[
                PermissionsGroup.SEND_PAYMENTS,
                PermissionsGroup.RECEIVE_PAYMENTS,
            ],
            access_token_expired=True,
        )
        request_event = harness.create_request_event()
        await handle_nip47_event(request_event)

        mock_nostr_send.assert_called_once()
        response_event = mock_nostr_send.call_args[0][0]
        content = harness.validate_response_event(response_event, request_event.id())
        assert content["result_type"] == Nip47RequestMethod.PAY_INVOICE.value
        assert content["error"]["code"] == ErrorCode.UNAUTHORIZED.name


@patch("nwc_backend.nostr_client.nostr_client.send_event", new_callable=AsyncMock)
async def test_failed__no_permission(
    mock_nostr_send: AsyncMock,
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        harness = Harness.prepare()
        await create_app_connection(
            granted_permissions_groups=[PermissionsGroup.READ_BALANCE],
            keys=harness.client_app_keys,
        )
        request_event = harness.create_request_event()
        await handle_nip47_event(request_event)

        mock_nostr_send.assert_called_once()
        response_event = mock_nostr_send.call_args[0][0]
        content = harness.validate_response_event(response_event, request_event.id())
        assert content["result_type"] == Nip47RequestMethod.PAY_INVOICE.value
        assert content["error"]["code"] == ErrorCode.RESTRICTED.name


@patch("nwc_backend.nostr_client.nostr_client.send_event", new_callable=AsyncMock)
async def test_failed__invalid_input_params(
    mock_nostr_send: AsyncMock,
    test_client: QuartClient,
) -> None:
    mock_nostr_send.return_value = SendEventOutput(
        id=EventId.from_hex(token_hex()),
        output=Output(success=["wss://relay.getalby.com/v1"], failed={}),
    )
    async with test_client.app.app_context():
        harness = Harness.prepare()
        await create_app_connection(
            granted_permissions_groups=[PermissionsGroup.SEND_PAYMENTS],
            keys=harness.client_app_keys,
        )
        request_event = harness.create_request_event(params={})
        await handle_nip47_event(request_event)

        mock_nostr_send.assert_called_once()
        response_event = mock_nostr_send.call_args[0][0]
        content = harness.validate_response_event(response_event, request_event.id())
        assert content["result_type"] == Nip47RequestMethod.PAY_INVOICE.value
        assert content["error"]["code"] == ErrorCode.OTHER.name


@patch("nwc_backend.nostr_client.nostr_client.send_event", new_callable=AsyncMock)
@patch.object(aiohttp.ClientSession, "post")
async def test_succeeded(
    mock_vasp_pay_invoice: Mock,
    mock_nostr_send: AsyncMock,
    test_client: QuartClient,
) -> None:
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_vasp_pay_invoice.return_value.__aenter__.return_value = mock_response

    response_id = EventId.from_hex(token_hex())
    mock_nostr_send.return_value = SendEventOutput(
        id=response_id,
        output=Output(success=["wss://relay.getalby.com/v1"], failed={}),
    )

    async with test_client.app.app_context():
        harness = Harness.prepare()
        app_connection = await create_app_connection(
            granted_permissions_groups=[PermissionsGroup.SEND_PAYMENTS],
            keys=harness.client_app_keys,
        )
        request_event = harness.create_request_event()
        await handle_nip47_event(request_event)

        mock_nostr_send.assert_called_once()
        response_event = mock_nostr_send.call_args[0][0]
        content = harness.validate_response_event(response_event, request_event.id())
        assert content["result_type"] == Nip47RequestMethod.PAY_INVOICE.value
        assert content["result"] == vasp_response

        # Check db store
        result = await db.session.execute(
            select(Nip47Request)
            .filter_by(event_id=request_event.id().to_hex())
            .limit(1)
        )
        request = result.scalars().one()
        assert request.app_connection_id == app_connection.id
        assert request.method == Nip47RequestMethod.PAY_INVOICE
        assert request.params == harness.get_default_request_params()
        assert request.response_event_id == response_id.to_hex()
        assert request.response_result == vasp_response
        assert request.response_error_code is None


@patch("nwc_backend.nostr_client.nostr_client.send_event", new_callable=AsyncMock)
@patch.object(aiohttp.ClientSession, "post")
async def test_failed__vasp_error_response(
    mock_vasp_pay_invoice: Mock,
    mock_nostr_send: AsyncMock,
    test_client: QuartClient,
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {
            "code": VaspErrorCode.PAYMENT_FAILED.name,
            "message": "Invoice has already been paid.",
        }
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_vasp_pay_invoice.return_value.__aenter__.return_value = mock_response

    mock_nostr_send.return_value = SendEventOutput(
        id=EventId.from_hex(token_hex()),
        output=Output(success=["wss://relay.getalby.com/v1"], failed={}),
    )

    async with test_client.app.app_context():
        harness = Harness.prepare()
        await create_app_connection(
            granted_permissions_groups=[PermissionsGroup.SEND_PAYMENTS],
            keys=harness.client_app_keys,
        )
        request_event = harness.create_request_event()
        await handle_nip47_event(request_event)

        mock_nostr_send.assert_called_once()
        response_event = mock_nostr_send.call_args[0][0]
        content = harness.validate_response_event(response_event, request_event.id())
        assert content["error"]["code"] == vasp_response.code.value
        assert content["error"]["message"] == vasp_response.message


@patch("nwc_backend.nostr_client.nostr_client.send_event", new_callable=AsyncMock)
@patch.object(aiohttp.ClientSession, "post")
async def test_duplicate_event(
    mock_vasp_pay_invoice: Mock,
    mock_nostr_send: AsyncMock,
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        harness = Harness.prepare()
        await create_app_connection(
            granted_permissions_groups=[PermissionsGroup.SEND_PAYMENTS],
            keys=harness.client_app_keys,
        )
        request_event = harness.create_request_event()
        nip47_event = await create_nip47_request(event_id=request_event.id().to_hex())

    async with test_client.app.app_context():
        await handle_nip47_event(request_event)

        mock_nostr_send.assert_not_called()
        mock_vasp_pay_invoice.assert_not_called()

    async with test_client.app.app_context():
        result = await db.session.execute(select(Nip47Request))
        request = result.scalars().one()
        assert request.id == nip47_event.id
