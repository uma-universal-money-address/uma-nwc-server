# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from datetime import datetime, timezone

from quart import request, session
from werkzeug import Response as WerkzeugResponse

from nwc_backend.db import db
from nwc_backend.models.nwc_connection import NWCConnection


async def disable_spending_limit() -> WerkzeugResponse:
    user_id = session.get("user_id")
    if not user_id:
        return WerkzeugResponse("User not authenticated", status=401)

    data = await request.get_json()
    connection_id = data.get("connectionId")
    if not connection_id:
        return WerkzeugResponse("Missing connectionId", status=400)

    connection = await db.session.get(NWCConnection, connection_id)
    if not connection or connection.user_id != user_id:
        return WerkzeugResponse("Invalid connectionId", status=400)

    if not connection.spending_limit:
        return WerkzeugResponse(
            "The connection has not enabled spending limit", status=400
        )

    connection.spending_limit.end_time = datetime.now(timezone.utc)
    connection.spending_limit_id = None
    await db.session.commit()
    return WerkzeugResponse(status=200)
