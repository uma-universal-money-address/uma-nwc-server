# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timedelta, timezone
from secrets import token_hex
from typing import Any, Optional
from uuid import uuid4

from nostr_sdk import Keys

from nwc_backend.db import db
from nwc_backend.models.app_connection import AppConnection
from nwc_backend.models.app_connection_status import AppConnectionStatus
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import PermissionsGroup
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.models.spending_cycle_quote import SpendingCycleQuote
from nwc_backend.models.spending_limit import SpendingLimit, SpendingLimitFrequency
from nwc_backend.models.user import User


async def create_user() -> User:
    user = User(
        id=uuid4(), vasp_user_id=str(uuid4()), uma_address=f"$test_{uuid4()}@uma.me"
    )
    db.session.add(user)
    await db.session.commit()
    return user


async def create_client_app() -> ClientApp:
    nostr_pubkey = Keys.generate().public_key().to_hex()
    identity_relay = "wss://myrelay.info"
    client_app = ClientApp(
        id=uuid4(),
        client_id=f"{nostr_pubkey} {identity_relay}",
        app_name="Blue Drink",
        display_name="Blue Drink",
    )
    db.session.add(client_app)
    await db.session.commit()
    return client_app


async def create_nwc_connection(
    granted_permissions_groups: list[PermissionsGroup] = [
        PermissionsGroup.RECEIVE_PAYMENTS,
        PermissionsGroup.SEND_PAYMENTS,
    ],
) -> NWCConnection:
    user = await create_user()
    client_app = await create_client_app()
    nwc_connection = NWCConnection(
        id=uuid4(),
        client_app=client_app,
        user=user,
        granted_permissions_groups=[
            command.value for command in granted_permissions_groups
        ],
        long_lived_vasp_token=token_hex(),
        connection_expires_at=int(
            (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
        ),
    )
    db.session.add(nwc_connection)
    await db.session.commit()
    return nwc_connection


async def create_app_connection(
    nwc_connection: Optional[NWCConnection] = None,
    granted_permissions_groups: list[PermissionsGroup] = [
        PermissionsGroup.RECEIVE_PAYMENTS,
        PermissionsGroup.SEND_PAYMENTS,
    ],
    keys: Optional[Keys] = None,
    access_token_expired: bool = False,
) -> AppConnection:
    nwc_connection = nwc_connection or await create_nwc_connection(
        granted_permissions_groups
    )
    keys = keys or Keys.generate()
    now = datetime.now(timezone.utc)
    if access_token_expired:
        access_token_expires_at = now - timedelta(days=30)
    else:
        access_token_expires_at = now + timedelta(days=30)
    app_connection = AppConnection(
        id=uuid4(),
        nwc_connection=nwc_connection,
        nostr_pubkey=keys.public_key().to_hex(),
        access_token=keys.secret_key().to_hex(),
        access_token_expires_at=int(access_token_expires_at.timestamp()),
        refresh_token=token_hex(),
        refresh_token_expires_at=int((now + timedelta(days=120)).timestamp()),
        authorization_code=token_hex(),
        authorization_code_expires_at=int((now + timedelta(minutes=10)).timestamp()),
        status=AppConnectionStatus.ACTIVE,
    )

    db.session.add(app_connection)
    await db.session.commit()
    return app_connection


async def create_spending_limit(
    nwc_connection: Optional[NWCConnection] = None,
    frequency: SpendingLimitFrequency = SpendingLimitFrequency.MONTHLY,
    amount: int = 100,
    currency_code: str = "USD",
) -> SpendingLimit:
    nwc_connection = nwc_connection or await create_nwc_connection()
    spending_limit = SpendingLimit(
        id=uuid4(),
        nwc_connection_id=nwc_connection.id,
        currency_code=currency_code,
        amount=amount,
        frequency=frequency,
        start_time=datetime.now(timezone.utc),
    )
    nwc_connection.spending_limit = spending_limit
    db.session.add(spending_limit)
    await db.session.commit()
    return spending_limit


async def create_nip47_request(
    app_connection: Optional[AppConnection] = None,
    params: Optional[dict[str, Any]] = None,
    event_id: Optional[str] = None,
) -> Nip47Request:
    if params is None:
        params = {
            "invoice": "lnbcrt1pjrsa37pp50geu5vxkzn4ddc4hmfkz9x308tw9lrrqtktz2hpm0rccjyhcyp5qdqh2d68yetpd45kueeqv3jk6mccqzpgxq9z0rgqsp5ge2rdw0tzvakxslmtvfmqf2fr7eucg9ughps5vdvp6fm2utk20rs9q8pqqqssqjs3k4nzrzg2nu9slu9c3srv2ae8v69ge097q9seukyw2nger8arj93m6erz8u657hfdzztfmc55wjjm9k337krl00fyw6s9nnwaafaspcqp2uv"
        }
    app_connection = app_connection or await create_app_connection()
    nip47_request = Nip47Request(
        id=uuid4(),
        app_connection=app_connection,
        event_id=event_id or token_hex(),
        method=Nip47RequestMethod.PAY_INVOICE,
        params=params,
        response_event_id=token_hex(),
        response_result={
            "preimage": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        },
    )
    db.session.add(nip47_request)
    await db.session.commit()
    return nip47_request


async def create_nip47_request_with_spending_limit(
    spending_limit_currency_code,
    spending_limit_currency_amount,
    params: dict[str, Any],
) -> Nip47Request:
    nwc_connection = await create_nwc_connection()
    await create_spending_limit(
        nwc_connection=nwc_connection,
        currency_code=spending_limit_currency_code,
        amount=spending_limit_currency_amount,
    )
    app_connection = await create_app_connection(nwc_connection=nwc_connection)
    return await create_nip47_request(app_connection=app_connection, params=params)


async def create_spending_cycle() -> SpendingCycle:
    spending_limit = await create_spending_limit()
    cycle_length = SpendingLimitFrequency.get_cycle_length(spending_limit.frequency)
    spending_cycle = SpendingCycle(
        id=uuid4(),
        spending_limit_id=spending_limit.id,
        limit_currency=spending_limit.currency_code,
        limit_amount=spending_limit.amount,
        start_time=spending_limit.start_time,
        end_time=(spending_limit.start_time + cycle_length) if cycle_length else None,
        total_spent=0,
        total_spent_on_hold=0,
    )
    db.session.add(spending_cycle)
    await db.session.commit()
    return spending_cycle


async def create_spending_cycle_quote(
    sending_currency_code: str = "USD", sending_currency_amount: int = 10_00
) -> SpendingCycleQuote:
    nip47_request = await create_nip47_request()
    quote = SpendingCycleQuote(
        id=uuid4(),
        nip47_request_id=nip47_request.id,
        payment_hash=token_hex(),
        sending_currency_code=sending_currency_code,
        sending_currency_amount=sending_currency_amount,
    )
    db.session.add(quote)
    await db.session.commit()
    return quote
