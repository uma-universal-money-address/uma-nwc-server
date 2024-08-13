# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
import logging
from datetime import datetime, timezone

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Event, Nip47Error, TagKind, nip04_decrypt
from pydantic_core import ValidationError as PydanticValidationError

from nwc_backend.configs.nostr_config import NostrConfig
from nwc_backend.event_handlers.event_builder import (
    create_nip47_error_response,
    create_nip47_response,
)
from nwc_backend.event_handlers.execute_quote_handler import execute_quote
from nwc_backend.event_handlers.fetch_quote_handler import fetch_quote
from nwc_backend.event_handlers.get_balance_handler import get_balance
from nwc_backend.event_handlers.get_info_handler import get_info
from nwc_backend.event_handlers.list_transactions_handler import list_transactions
from nwc_backend.event_handlers.lookup_invoice_handler import lookup_invoice
from nwc_backend.event_handlers.lookup_user_handler import lookup_user
from nwc_backend.event_handlers.make_invoice_handler import make_invoice
from nwc_backend.event_handlers.pay_invoice_handler import pay_invoice
from nwc_backend.event_handlers.pay_to_address_handler import pay_to_address
from nwc_backend.exceptions import Nip47RequestException
from nwc_backend.models.app_connection import AppConnection
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.nostr_client import nostr_client


async def handle_nip47_event(event: Event) -> None:
    app_connection = await AppConnection.from_nostr_pubkey(event.author().to_hex())
    if not app_connection:
        error_response = create_nip47_error_response(
            event=event,
            method=None,
            error=Nip47Error(
                code=ErrorCode.UNAUTHORIZED,
                message="The public key for nwc connection is not recognized.",
            ),
        )
        await nostr_client.send_event(error_response)
        return

    now = datetime.now(timezone.utc)
    if app_connection.is_access_token_expired():
        error_response = create_nip47_error_response(
            event=event,
            method=None,
            error=Nip47Error(
                code=ErrorCode.UNAUTHORIZED,
                message="The nwc connection secret has expired.",
            ),
        )
        await nostr_client.send_event(error_response)
        return

    expiration = event.get_tag_content(TagKind.EXPIRATION())  # pyre-ignore[6]
    if expiration and datetime.fromtimestamp(float(expiration), timezone.utc) < now:
        logging.debug("Event ignored: expired at %s.", expiration)
        return

    content = json.loads(
        nip04_decrypt(
            secret_key=NostrConfig.instance().identity_privkey,
            public_key=event.author(),
            encrypted_content=event.content(),
        )
    )

    method = Nip47RequestMethod(content["method"])
    if not app_connection.has_command_permission(method):
        error_response = create_nip47_error_response(
            event=event,
            method=None,
            error=Nip47Error(
                code=ErrorCode.UNAUTHORIZED,
                message=f"No permission for request method {method.name}.",
            ),
        )
        await nostr_client.send_event(error_response)
        return

    params = content["params"]

    nip47_request = await Nip47Request.create_and_save(
        app_connection_id=app_connection.id,
        event_id=event.id().to_hex(),
        method=method,
        params=params,
    )

    uma_access_token = app_connection.nwc_connection.long_lived_vasp_token
    try:
        match method:
            case Nip47RequestMethod.EXECUTE_QUOTE:
                response = await execute_quote(uma_access_token, nip47_request)
            case Nip47RequestMethod.FETCH_QUOTE:
                response = await fetch_quote(uma_access_token, nip47_request)
            case Nip47RequestMethod.GET_BALANCE:
                response = await get_balance(uma_access_token, nip47_request)
            case Nip47RequestMethod.GET_INFO:
                response = await get_info(uma_access_token, nip47_request)
            case Nip47RequestMethod.LIST_TRANSACTIONS:
                response = await list_transactions(uma_access_token, nip47_request)
            case Nip47RequestMethod.LOOKUP_INVOICE:
                response = await lookup_invoice(uma_access_token, nip47_request)
            case Nip47RequestMethod.LOOKUP_USER:
                response = await lookup_user(uma_access_token, nip47_request)
            case Nip47RequestMethod.MAKE_INVOICE:
                response = await make_invoice(uma_access_token, nip47_request)
            case Nip47RequestMethod.PAY_INVOICE:
                response = await pay_invoice(uma_access_token, nip47_request)
            case Nip47RequestMethod.PAY_TO_ADDRESS:
                response = await pay_to_address(uma_access_token, nip47_request)
            case _:
                response = Nip47Error(
                    code=ErrorCode.NOT_IMPLEMENTED,
                    message=f"Method {method} is not supported.",
                )
    except Exception as ex:
        logging.exception("Request %s %s failed", method, str(nip47_request.id))

        if isinstance(ex, PydanticValidationError):
            response = Nip47Error(
                code=ErrorCode.OTHER,
                message=str(ex),
            )
        elif isinstance(ex, Nip47RequestException):
            response = Nip47Error(
                code=ex.error_code,
                message=ex.error_message,
            )
        elif isinstance(ex, ClientResponseError):
            response = Nip47Error(
                code=ErrorCode.OTHER,
                message=str(ex),
            )
        else:
            response = Nip47Error(
                code=ErrorCode.INTERNAL,
                message=str(ex),
            )

    if isinstance(response, Nip47Error):
        response_event = create_nip47_error_response(
            event=event, method=method, error=response
        )
    else:
        response = response.to_dict()
        response_event = create_nip47_response(
            event=event, method=method, result=response
        )

    output = await nostr_client.send_event(response_event)
    await nip47_request.update_response_and_save(
        response_event_id=output.id.to_hex(), response=response
    )
