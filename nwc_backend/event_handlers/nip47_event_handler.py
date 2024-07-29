# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
import logging
from datetime import datetime, timezone
from enum import Enum

from nostr_sdk import Event, TagKind, nip04_decrypt

from nwc_backend.configs.nostr_config import nostr_config
from nwc_backend.event_handlers.execute_quote_handler import execute_quote
from nwc_backend.event_handlers.fetch_quote_handler import fetch_quote
from nwc_backend.event_handlers.get_balance_handler import get_balance
from nwc_backend.event_handlers.get_info_handler import get_info
from nwc_backend.event_handlers.list_transactions_handler import list_transactions
from nwc_backend.event_handlers.lookup_invoice_handler import lookup_invoice
from nwc_backend.event_handlers.lookup_user_handler import lookup_user
from nwc_backend.event_handlers.make_invoice_handler import make_invoice
from nwc_backend.event_handlers.pay_invoice_handler import pay_invoice
from nwc_backend.event_handlers.pay_keysend_handler import pay_keysend
from nwc_backend.event_handlers.pay_to_address_handler import pay_to_address


class Nip47EventMethod(Enum):
    PAY_INVOICE = "pay_invoice"
    MAKE_INVOICE = "make_invoice"
    LOOKUP_INVOICE = "lookup_invoice"
    GET_BALANCE = "get_balance"
    GET_INFO = "get_info"
    LIST_TRANSACTIONS = "list_transactions"
    PAY_KEYSEND = "pay_keysend"
    LOOKUP_USER = "lookup_user"
    FETCH_QUOTE = "fetch_quote"
    EXECUTE_QUOTE = "execute_quote"
    PAY_TO_ADDRESS = "pay_to_address"


async def handle_nip47_event(event: Event) -> None:
    expiration = event.get_tag_content(TagKind.EXPIRATION())  # pyre-ignore[6]
    if expiration and datetime.fromtimestamp(
        float(expiration), timezone.utc
    ) < datetime.now(timezone.utc):
        logging.debug("Event ignored: expired at %s.", expiration)
        return

    # TODO (yunyu): verify event.author is a stored connection pubkey

    content = json.loads(
        nip04_decrypt(
            secret_key=nostr_config.identity_privkey,
            public_key=event.author(),
            encrypted_content=event.content(),
        )
    )

    method = Nip47EventMethod(content["method"])
    # TODO (yunyu): verify method is allowed in permission

    params = content["params"]
    match method:
        case Nip47EventMethod.PAY_INVOICE:
            await pay_invoice(params)
        case Nip47EventMethod.MAKE_INVOICE:
            await make_invoice(params)
        case Nip47EventMethod.LOOKUP_INVOICE:
            await lookup_invoice(params)
        case Nip47EventMethod.GET_BALANCE:
            await get_balance(params)
        case Nip47EventMethod.GET_INFO:
            await get_info(params)
        case Nip47EventMethod.LIST_TRANSACTIONS:
            await list_transactions(params)
        case Nip47EventMethod.PAY_KEYSEND:
            await pay_keysend(params)
        case Nip47EventMethod.LOOKUP_USER:
            await lookup_user(params)
        case Nip47EventMethod.FETCH_QUOTE:
            await fetch_quote(params)
        case Nip47EventMethod.EXECUTE_QUOTE:
            await execute_quote(params)
        case Nip47EventMethod.PAY_TO_ADDRESS:
            await pay_to_address(params)
