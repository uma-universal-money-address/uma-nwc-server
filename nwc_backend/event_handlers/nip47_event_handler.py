# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
import logging
from datetime import datetime, timezone

from nostr_sdk import ErrorCode, Event, Nip47Error, TagKind, nip04_decrypt

from nwc_backend.configs.nostr_config import nostr_config
from nwc_backend.event_handlers.event_builder import create_nip47_error_response
from nwc_backend.event_handlers.execute_quote_handler import execute_quote
from nwc_backend.event_handlers.fetch_quote_handler import fetch_quote
from nwc_backend.event_handlers.get_balance_handler import get_balance
from nwc_backend.event_handlers.get_info_handler import get_info
from nwc_backend.event_handlers.list_transactions_handler import list_transactions
from nwc_backend.event_handlers.lookup_invoice_handler import lookup_invoice
from nwc_backend.event_handlers.lookup_user_handler import lookup_user
from nwc_backend.event_handlers.make_invoice_handler import make_invoice
from nwc_backend.event_handlers.nip47_request_method import Nip47RequestMethod
from nwc_backend.event_handlers.pay_invoice_handler import pay_invoice
from nwc_backend.event_handlers.pay_keysend_handler import pay_keysend
from nwc_backend.event_handlers.pay_to_address_handler import pay_to_address
from nwc_backend.models.app_connection import AppConnection
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

    expiration = event.get_tag_content(TagKind.EXPIRATION())  # pyre-ignore[6]
    if expiration and datetime.fromtimestamp(
        float(expiration), timezone.utc
    ) < datetime.now(timezone.utc):
        logging.debug("Event ignored: expired at %s.", expiration)
        return

    content = json.loads(
        nip04_decrypt(
            secret_key=nostr_config.identity_privkey,
            public_key=event.author(),
            encrypted_content=event.content(),
        )
    )

    method = Nip47RequestMethod(content["method"])
    # TODO (yunyu): verify method is allowed in permission

    params = content["params"]
    match method:
        case Nip47RequestMethod.PAY_INVOICE:
            await pay_invoice(params)
        case Nip47RequestMethod.MAKE_INVOICE:
            await make_invoice(params)
        case Nip47RequestMethod.LOOKUP_INVOICE:
            await lookup_invoice(params)
        case Nip47RequestMethod.GET_BALANCE:
            await get_balance(params)
        case Nip47RequestMethod.GET_INFO:
            await get_info(params)
        case Nip47RequestMethod.LIST_TRANSACTIONS:
            await list_transactions(params)
        case Nip47RequestMethod.PAY_KEYSEND:
            await pay_keysend(params)
        case Nip47RequestMethod.LOOKUP_USER:
            await lookup_user(params)
        case Nip47RequestMethod.FETCH_QUOTE:
            await fetch_quote(params)
        case Nip47RequestMethod.EXECUTE_QUOTE:
            await execute_quote(params)
        case Nip47RequestMethod.PAY_TO_ADDRESS:
            await pay_to_address(params)
