import json
from uuid import uuid4

from nostr_sdk import Keys
from quart import current_app, request, session
from werkzeug import Response as WerkzeugResponse

from nwc_backend.api_handlers.connection_initializer import initialize_connection_data
from nwc_backend.db import db
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.vasp_jwt import VaspJwt


async def create_manual_connection() -> WerkzeugResponse:
    short_lived_vasp_token = session.get("short_lived_vasp_token")
    if not short_lived_vasp_token:
        return WerkzeugResponse("Unauthorized", status=401)
    vasp_jwt = VaspJwt.from_jwt(short_lived_vasp_token)
    keypair = Keys.generate()
    request_data = await request.get_json()
    name = request_data.get("customName")
    if not name:
        return WerkzeugResponse(
            "customName is required for manual connections", status=400
        )

    nwc_connection = NWCConnection(
        id=uuid4(),
        user_id=vasp_jwt.user_id,
        granted_permissions_groups=[],  # permissions will be added later
        nostr_pubkey=keypair.public_key().to_hex(),
        custom_name=name,
    )

    db.session.add(nwc_connection)
    await db.session.commit()

    await initialize_connection_data(
        nwc_connection,
        request_data=request_data,
        short_lived_vasp_token=short_lived_vasp_token,
    )
    secret = keypair.secret_key().to_hex()

    return WerkzeugResponse(
        json.dumps(
            {
                "connectionId": str(nwc_connection.id),
                "pairingUri": await nwc_connection.get_nwc_connection_uri(secret),
            }
        ),
        content_type="application/json",
    )
