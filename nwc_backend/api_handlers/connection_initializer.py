from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import requests
from quart import current_app

from nwc_backend.db import db
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import (
    PERMISSIONS_GROUP_TO_METHODS,
    PermissionsGroup,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.spending_limit_frequency import SpendingLimitFrequency


async def initialize_connection_data(
    nwc_connection: NWCConnection,
    request_data: dict[str, Any],
    short_lived_vasp_token: str,
):
    uma_vasp_token_exchange_url = current_app.config["UMA_VASP_TOKEN_EXCHANGE_URL"]
    permissions = request_data.get("permissions")
    currency_code = request_data.get("currencyCode")
    amount_in_lowest_denom = request_data.get("amountInLowestDenom")
    limit_enabled = request_data.get("limitEnabled")
    limit_frequency = request_data.get("limitFrequency")
    expiration = request_data.get("expiration")
    custom_name = request_data.get("customName")

    if expiration:
        expires_at = datetime.fromisoformat(expiration)
        nwc_connection.connection_expires_at = round(expires_at.timestamp())

    if custom_name:
        nwc_connection.custom_name = custom_name

    if limit_enabled:
        limit_frequency = (
            SpendingLimitFrequency(limit_frequency)
            if limit_frequency
            else SpendingLimitFrequency.NONE
        )
        spending_limit = SpendingLimit(
            id=uuid4(),
            nwc_connection_id=nwc_connection.id,
            currency_code=currency_code or "SAT",
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
    await db.session.commit()
