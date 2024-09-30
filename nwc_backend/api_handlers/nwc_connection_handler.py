# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import requests
from nostr_sdk import Keys
from quart import Response, current_app, request, session
from sqlalchemy.sql import func, select

from nwc_backend.db import db
from nwc_backend.exceptions import InvalidApiParamsException
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.outgoing_payment import OutgoingPayment, PaymentStatus
from nwc_backend.models.permissions_grouping import (
    PERMISSIONS_GROUP_TO_METHODS,
    PermissionsGroup,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.spending_limit_frequency import SpendingLimitFrequency
from nwc_backend.models.user import User
from nwc_backend.models.vasp_jwt import VaspJwt
from nwc_backend.vasp_client import VaspUmaClient


class NoSupportedCurrenciesException(Exception):
    pass


async def create_manual_connection() -> Response:
    short_lived_vasp_token = session.get("short_lived_vasp_token")
    if not short_lived_vasp_token:
        bearer_token = request.headers.get("Authorization")
        if not bearer_token:
            return Response("Unauthorized", status=401)
        short_lived_vasp_token = bearer_token.split("Bearer ")[-1]

    if not short_lived_vasp_token:
        return Response("Unauthorized", status=401)
    vasp_jwt = VaspJwt.from_jwt(short_lived_vasp_token)
    keypair = Keys.generate()
    request_data = await request.get_json()
    name = request_data.get("name")
    if not name:
        return Response("name is required for manual connections", status=400)

    user = await User.from_vasp_user_id(vasp_jwt.user_id)
    if not user:
        user = User(
            id=uuid4(),
            vasp_user_id=vasp_jwt.user_id,
            uma_address=vasp_jwt.uma_address,
        )
        db.session.add(user)

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
            short_lived_vasp_token=short_lived_vasp_token,
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
    short_lived_vasp_token = session.get("short_lived_vasp_token")
    if not short_lived_vasp_token:
        return Response("Unauthorized", status=401)

    nwc_connection = NWCConnection(
        id=uuid4(),
        user_id=session["user_id"],
        client_app_id=session["client_app_id"],
        redirect_uri=session["redirect_uri"],
        code_challenge=session["code_challenge"],
    )
    try:
        await _initialize_connection_data(
            nwc_connection,
            request_data=await request.get_json(),
            short_lived_vasp_token=short_lived_vasp_token,
        )
    except InvalidApiParamsException as ex:
        return Response(ex.message, status=400)
    except NoSupportedCurrenciesException:
        return Response("Wallet has no supported currency", status=404)

    auth_code = nwc_connection.create_oauth_auth_code()
    db.session.add(nwc_connection)
    await db.session.commit()

    return Response(
        json.dumps(
            {
                "code": auth_code,
                "state": session["client_state"],
            }
        )
    )


async def _initialize_connection_data(
    nwc_connection: NWCConnection,
    request_data: dict[str, Any],
    short_lived_vasp_token: str,
) -> None:
    uma_vasp_token_exchange_url = current_app.config["UMA_VASP_TOKEN_EXCHANGE_URL"]
    permissions = request_data.get("permissions")
    currency_code = request_data.get("currencyCode")
    amount_in_lowest_denom = request_data.get("amountInLowestDenom")
    limit_enabled = request_data.get("limitEnabled")
    limit_frequency = request_data.get("limitFrequency")
    expiration = request_data.get("expiration")

    if expiration:
        expires_at = datetime.fromisoformat(expiration)
        nwc_connection.connection_expires_at = round(expires_at.timestamp())

    preferred_currencies = (
        await VaspUmaClient.instance().get_info(access_token=short_lived_vasp_token)
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
    for permission in all_granted_granular_permissions:
        if permission not in vasp_supported_commands:
            all_granted_granular_permissions.remove(permission)

    # save the long lived token in the db and create the app connection
    response = requests.post(
        uma_vasp_token_exchange_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + short_lived_vasp_token,
        },
        json={
            "permissions": list(all_granted_granular_permissions),
            "expiration": nwc_connection.connection_expires_at,
        },
    )
    response.raise_for_status()
    long_lived_vasp_token = response.json()["token"]

    nwc_connection.long_lived_vasp_token = long_lived_vasp_token


async def get_connection(connection_id: str) -> Response:
    user_id = session.get("user_id")
    if not user_id:
        return Response("User not authenticated", status=401)

    connection = await db.session.get(NWCConnection, connection_id)
    if not connection or connection.user_id != user_id:
        return Response("Connection not found", status=404)
    response = await connection.to_dict()
    return Response(json.dumps(response), status=200)


async def get_all_connections() -> Response:
    user_id = session.get("user_id")
    if not user_id:
        return Response("User not authenticated", status=401)

    result = await db.session.execute(
        select(NWCConnection).filter(NWCConnection.user_id == user_id)
    )
    response = []
    for connection in result.scalars():
        response.append(await connection.to_dict())
    return Response(json.dumps(response), status=200)


async def get_all_outgoing_payments(connection_id: str) -> Response:
    user_id = session.get("user_id")
    if not user_id:
        return Response("User not authenticated", status=401)

    connection = await db.session.get(NWCConnection, connection_id)
    if not connection or connection.user_id != user_id:
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
