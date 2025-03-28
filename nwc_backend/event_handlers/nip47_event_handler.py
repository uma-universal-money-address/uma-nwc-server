# pyre-strict

import json
import logging
from datetime import datetime, timezone

from nostr_sdk import (
    ErrorCode,
    Event,
    Nip47Error,
    TagKind,
    nip04_decrypt,
    nip44_decrypt,
)
from pydantic_core import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError

from nwc_backend.event_handlers.event_builder import (
    create_nip47_error_response,
    create_nip47_response,
)
from nwc_backend.event_handlers.execute_quote_handler import execute_quote
from nwc_backend.event_handlers.fetch_quote_handler import fetch_quote
from nwc_backend.event_handlers.get_balance_handler import get_balance
from nwc_backend.event_handlers.get_budget_handler import get_budget
from nwc_backend.event_handlers.get_info_handler import get_info
from nwc_backend.event_handlers.list_transactions_handler import list_transactions
from nwc_backend.event_handlers.lookup_invoice_handler import lookup_invoice
from nwc_backend.event_handlers.lookup_user_handler import lookup_user
from nwc_backend.event_handlers.make_invoice_handler import make_invoice
from nwc_backend.event_handlers.pay_invoice_handler import pay_invoice
from nwc_backend.event_handlers.pay_keysend_handler import pay_keysend
from nwc_backend.event_handlers.pay_to_address_handler import pay_to_address
from nwc_backend.exceptions import Nip47RequestException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.nostr.nostr_client import nostr_client
from nwc_backend.nostr.nostr_config import NostrConfig
from nwc_backend.nostr.encryption import is_encryption_supported


async def handle_nip47_event(event: Event) -> None:
    expiration = event.get_tag_content(TagKind.EXPIRATION())  # pyre-ignore[6]
    if expiration and datetime.fromtimestamp(
        float(expiration), timezone.utc
    ) < datetime.now(timezone.utc):
        logging.debug("Event ignored: expired at %s.", expiration)
        return

    is_nip04_encrypted = "?iv=" in event.content()
    content = json.loads(
        nip04_decrypt(
            secret_key=NostrConfig.instance().identity_keys.secret_key(),
            public_key=event.author(),
            encrypted_content=event.content(),
        )
        if is_nip04_encrypted
        else nip44_decrypt(
            secret_key=NostrConfig.instance().identity_keys.secret_key(),
            public_key=event.author(),
            payload=event.content(),
        )
    )

    nwc_connection = await NWCConnection.from_nostr_pubkey(event.author().to_hex())
    if not nwc_connection:
        error_response = create_nip47_error_response(
            event=event,
            method=None,
            error=Nip47Error(
                code=ErrorCode.UNAUTHORIZED,
                message="The public key for nwc connection is not recognized.",
            ),
            use_nip44=not is_nip04_encrypted,
        )
        await nostr_client.send_event(error_response)
        return

    method = Nip47RequestMethod(content["method"])

    try:
        _check_encryption(event)
    except Nip47RequestException as ex:
        error_response = create_nip47_error_response(
            event=event,
            method=method,
            error=Nip47Error(
                code=ex.error_code,
                message=ex.error_message,
            ),
            use_nip44=not is_nip04_encrypted,
        )
        await nostr_client.send_event(error_response)
        return

    if not nwc_connection.has_command_permission(method):
        error_response = create_nip47_error_response(
            event=event,
            method=method,
            error=Nip47Error(
                code=ErrorCode.RESTRICTED,
                message=f"No permission for request method {method.name}.",
            ),
            use_nip44=not is_nip04_encrypted,
        )
        await nostr_client.send_event(error_response)
        return

    if nwc_connection.is_oauth_access_token_expired():
        error_response = create_nip47_error_response(
            event=event,
            method=method,
            error=Nip47Error(
                code=ErrorCode.UNAUTHORIZED,
                message="The nwc connection secret has expired.",
            ),
            use_nip44=not is_nip04_encrypted,
        )
        await nostr_client.send_event(error_response)
        return

    params = content["params"]

    try:
        nip47_request = await Nip47Request.create_and_save(
            nwc_connection=nwc_connection,
            event_id=event.id().to_hex(),
            method=method,
            params=params,
        )
    except IntegrityError:
        logging.debug("Event %s has been processed already.", event.id().to_hex())
        return

    uma_access_token = nwc_connection.long_lived_vasp_token
    try:
        match method:
            case Nip47RequestMethod.EXECUTE_QUOTE:
                response = await execute_quote(uma_access_token, nip47_request)
            case Nip47RequestMethod.FETCH_QUOTE:
                response = await fetch_quote(uma_access_token, nip47_request)
            case Nip47RequestMethod.GET_BALANCE:
                response = await get_balance(uma_access_token, nip47_request)
            case Nip47RequestMethod.GET_BUDGET:
                response = await get_budget(uma_access_token, nip47_request)
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
            case Nip47RequestMethod.PAY_KEYSEND:
                response = await pay_keysend(uma_access_token, nip47_request)
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
        else:
            response = Nip47Error(
                code=ErrorCode.INTERNAL,
                message=str(ex),
            )

    if isinstance(response, Nip47Error):
        response_event = create_nip47_error_response(
            event=event,
            method=method,
            error=response,
            use_nip44=not is_nip04_encrypted,
        )
    else:
        response = response.to_dict()
        response_event = create_nip47_response(
            event=event,
            method=method,
            result=response,
            use_nip44=not is_nip04_encrypted,
        )

    output = await nostr_client.send_event(response_event)
    await nip47_request.update_response_and_save(
        response_event_id=output.id.to_hex(), response=response
    )


def _check_encryption(event: Event) -> None:
    is_nip04_encrypted = "?iv=" in event.content()
    encryption_tag = next(
        (tag for tag in event.tags() if tag.as_vec()[0] == "encryption"), None
    )
    selected_encryption = (
        encryption_tag.content() if encryption_tag else "nip04"
    ) or "nip04"

    if not is_encryption_supported(selected_encryption):
        raise Nip47RequestException(
            # TODO: Use ErrorCode.UNSUPPORTED_ENCRYPTION when added.
            error_code=ErrorCode.NOT_IMPLEMENTED,
            error_message=f"Unsupported encryption {selected_encryption}.",
        )

    if selected_encryption == "nip04" and not is_nip04_encrypted:
        raise Nip47RequestException(
            error_code=ErrorCode.OTHER,
            error_message="NIP04 encryption specified but NIP44 encryption is used.",
        )
    elif selected_encryption.startswith("nip44") and is_nip04_encrypted:
        raise Nip47RequestException(
            error_code=ErrorCode.OTHER,
            error_message="NIP44 encryption specified but NIP04 encryption is used.",
        )
