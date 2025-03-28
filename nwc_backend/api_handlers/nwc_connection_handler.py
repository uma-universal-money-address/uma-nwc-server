# pyre-strict

import json
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from nostr_sdk import Keys
from quart import Response, current_app, request
from sqlalchemy.sql import func, select

from nwc_backend.db import db
from nwc_backend.exceptions import InvalidApiParamsException
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.outgoing_payment import OutgoingPayment, PaymentStatus
from nwc_backend.models.permissions_grouping import (
    PERMISSIONS_GROUP_TO_METHODS,
    PermissionsGroup,
)
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.spending_limit_frequency import SpendingLimitFrequency
from nwc_backend.vasp_client import VaspUmaClient
from nwc_backend.wrappers import require_auth


class NoSupportedCurrenciesException(Exception):
    pass


async def create_manual_connection() -> Response:
    auth_state = require_auth(request)
    user = auth_state.user
    keypair = Keys.generate()
    request_data = await request.get_json()
    name = request_data.get("name")
    if not name:
        return Response("name is required for manual connections", status=400)

    nwc_connection = NWCConnection(
        id=uuid4(),
        user_id=user.id,
        nostr_pubkey=keypair.public_key().to_hex(),
        custom_name=name,
    )
    try:
        await _initialize_connection_data(
            nwc_connection,
            request_data=request_data,
            short_lived_vasp_token=auth_state.token,
        )
    except InvalidApiParamsException as ex:
        return Response(ex.message, status=400)
    except NoSupportedCurrenciesException:
        return Response("Wallet has no supported currency", status=404)

    db.session.add(nwc_connection)
    await db.session.commit()

    secret = keypair.secret_key().to_hex()
    return Response(
        json.dumps(
            {
                "connectionId": str(nwc_connection.id),
                "pairingUri": nwc_connection.get_nwc_connection_uri(secret),
            }
        ),
        content_type="application/json",
    )


async def create_client_app_connection() -> Response:
    auth_state = require_auth(request)
    request_data = await request.get_json()
    client_id = request_data["clientId"]
    client_app = await ClientApp.from_client_id(client_id)
    if not client_app:
        return Response("Client app not found", status=404)
    nwc_connection = NWCConnection(
        id=uuid4(),
        user_id=auth_state.user.id,
        client_app_id=client_app.id,
        redirect_uri=request_data["redirectUri"],
        code_challenge=request_data["codeChallenge"],
    )
    try:
        await _initialize_connection_data(
            nwc_connection,
            request_data=await request.get_json(),
            short_lived_vasp_token=auth_state.token,
        )
    except InvalidApiParamsException as ex:
        return Response(ex.message, status=400)
    except NoSupportedCurrenciesException:
        return Response("Wallet has no supported currency", status=404)

    auth_code = nwc_connection.create_oauth_auth_code()
    db.session.add(nwc_connection)
    await db.session.commit()

    return Response(json.dumps({"code": auth_code}))


async def _initialize_connection_data(
    nwc_connection: NWCConnection,
    request_data: dict[str, Any],
    short_lived_vasp_token: str,
) -> None:
    permissions = request_data.get("permissions")
    currency_code = request_data.get("currencyCode")
    amount_in_lowest_denom = request_data.get("amountInLowestDenom")
    limit_enabled = request_data.get("limitEnabled")
    limit_frequency = request_data.get("limitFrequency")
    expiration = request_data.get("expiration")

    if expiration:
        expires_at = datetime.fromisoformat(expiration)
        nwc_connection.connection_expires_at = round(expires_at.timestamp())

    vasp_uma_client = VaspUmaClient.instance()
    preferred_currencies = (
        await vasp_uma_client.get_info(access_token=short_lived_vasp_token)
    ).currencies
    if not preferred_currencies:
        raise NoSupportedCurrenciesException()

    if currency_code:
        preferred_currencies = [
            currency
            for currency in preferred_currencies
            if currency.currency.code == currency_code
        ]
        if not preferred_currencies:
            raise InvalidApiParamsException(
                "The currency of budget is not supported by user's wallet."
            )
    nwc_connection.budget_currency = preferred_currencies[0].currency

    if limit_enabled:
        limit_frequency = (
            SpendingLimitFrequency(limit_frequency)
            if limit_frequency
            else SpendingLimitFrequency.NONE
        )
        spending_limit = SpendingLimit(
            id=uuid4(),
            nwc_connection_id=nwc_connection.id,
            amount=amount_in_lowest_denom,
            frequency=limit_frequency,
            start_time=datetime.now(timezone.utc),
        )
        db.session.add(spending_limit)
        nwc_connection.spending_limit_id = spending_limit.id
    else:
        nwc_connection.spending_limit_id = None

    # the frontend will always send grouped permissions so we can directly save
    nwc_connection.granted_permissions_groups = permissions
    all_granted_granular_permissions = set()
    for permission in permissions:
        all_granted_granular_permissions.update(
            PERMISSIONS_GROUP_TO_METHODS[PermissionsGroup(permission)]
        )
    all_granted_granular_permissions.update(
        PERMISSIONS_GROUP_TO_METHODS[PermissionsGroup.ALWAYS_GRANTED]
    )
    vasp_supported_commands = current_app.config["VASP_SUPPORTED_COMMANDS"]
    all_granted_granular_permissions_list = [
        p for p in all_granted_granular_permissions if p in vasp_supported_commands
    ]

    # save the long lived token in the db and create the app connection
    long_lived_vasp_token = await vasp_uma_client.token_exchange(
        access_token=short_lived_vasp_token,
        permissions=all_granted_granular_permissions_list,
        expiration=nwc_connection.connection_expires_at,
    )
    nwc_connection.long_lived_vasp_token = long_lived_vasp_token


async def get_connection(connection_id: str) -> Response:
    auth_state = require_auth(request)

    connection = await db.session.get(NWCConnection, connection_id)
    if not connection or connection.user_id != auth_state.user.id:
        return Response("Connection not found", status=404)
    response = await connection.to_dict()
    return Response(json.dumps(response), status=200)


async def get_all_connections() -> Response:
    auth_state = require_auth(request)

    result = await db.session.execute(
        select(NWCConnection).filter(NWCConnection.user_id == auth_state.user.id)
    )
    response = []
    for connection in result.scalars():
        response.append(await connection.to_dict())
    return Response(json.dumps(response), status=200)


async def get_all_outgoing_payments(connection_id: str) -> Response:
    auth_state = require_auth(request)

    connection = await db.session.get(NWCConnection, connection_id)
    if not connection or connection.user_id != auth_state.user.id:
        return Response("Connection not found", status=404)

    if "limit" not in request.args:
        return Response("Limit needs to be set", status=400)

    limit = int(request.args["limit"])
    offset = int(request.args["offset"]) if "offset" in request.args else 0
    results = await db.session.execute(
        select(OutgoingPayment)
        .where(OutgoingPayment.nwc_connection_id == connection_id)
        .where(OutgoingPayment.status != PaymentStatus.FAILED)
        .order_by(OutgoingPayment.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    payments = results.scalars().all()
    response = {"transactions": [payment.to_dict() for payment in payments]}
    count = await db.session.scalar(
        select(func.count(OutgoingPayment.id))
        .where(OutgoingPayment.nwc_connection_id == connection_id)
        .where(OutgoingPayment.status != PaymentStatus.FAILED)
    )
    response["count"] = count - offset
    return Response(json.dumps(response), status=200)


async def update_connection(connection_id: str) -> Response:
    auth_state = require_auth(request)
    user_id = auth_state.user.id

    connection: NWCConnection = await db.session.get(NWCConnection, connection_id)
    if not connection or connection.user_id != user_id:
        return Response("Connection not found", status=404)
    data = await request.get_data()
    data = json.loads(data)
    amount_in_lowest_denom = data.get("amountInLowestDenom")
    limit_enabled = data.get("limitEnabled")
    limit_frequency = data.get("limitFrequency")
    expiration = data.get("expiration")
    status = data.get("status")

    if status and status == "Inactive":
        connection.connection_expires_at = int(datetime.now(timezone.utc).timestamp())
        await db.session.commit()
        return Response(json.dumps({"success": "Connection deleted"}), status=200)

    if not expiration:
        return Response("Expiration is required", status=400)
    connection.connection_expires_at = round(
        datetime.fromisoformat(expiration).timestamp()
    )

    current_spending_limit: Optional[SpendingLimit] = connection.spending_limit
    if limit_enabled:
        # amount_in_lowest_denom is required if limit is enabled
        try:
            amount_in_lowest_denom = int(amount_in_lowest_denom)
        except ValueError:
            return Response("Invalid amount", status=400)
        new_limit_frequency = (
            SpendingLimitFrequency(limit_frequency)
            if limit_frequency
            else SpendingLimitFrequency.NONE
        )

        if not current_spending_limit:
            spending_limit = SpendingLimit(
                id=uuid4(),
                nwc_connection_id=connection_id,
                amount=amount_in_lowest_denom,
                frequency=new_limit_frequency,
                start_time=datetime.now(timezone.utc),
            )
            db.session.add(spending_limit)
            connection.spending_limit_id = spending_limit.id
        elif limit_frequency != current_spending_limit.frequency.value:
            # if limit frequency is changed, we need to end the current limit and cycle and create a new one
            current_spending_limit.end_time = datetime.now(timezone.utc)
            cycle: Optional[SpendingCycle] = (
                await current_spending_limit.get_current_spending_cycle()
            )
            if cycle:
                cycle.end_time = datetime.now(timezone.utc)

            spending_limit = SpendingLimit(
                id=uuid4(),
                nwc_connection_id=connection_id,
                amount=amount_in_lowest_denom or current_spending_limit.amount,
                frequency=new_limit_frequency,
                start_time=datetime.now(timezone.utc),
            )
            db.session.add(spending_limit)
            connection.spending_limit_id = spending_limit.id
        elif amount_in_lowest_denom != current_spending_limit.amount:
            # if limit amount is changed, we need to update the current limit and cycle amounts
            current_spending_limit.amount = amount_in_lowest_denom
            cycle: Optional[SpendingCycle] = (
                await current_spending_limit.get_current_spending_cycle()
            )
            if cycle:
                cycle.limit_amount = amount_in_lowest_denom

    else:
        if current_spending_limit:
            current_spending_limit.end_time = datetime.now(timezone.utc)
            cycle: Optional[SpendingCycle] = (
                await current_spending_limit.get_current_spending_cycle()
            )
            if cycle:
                cycle.end_time = datetime.now(timezone.utc)
            connection.spending_limit_id = None

    await db.session.commit()
    connection = await db.session.get(NWCConnection, connection_id)
    response = await connection.to_dict()
    return Response(json.dumps(response), status=200)
