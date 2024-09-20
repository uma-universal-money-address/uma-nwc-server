# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json

from quart import Response, request, session

from nwc_backend.nostr.client_app_identity_lookup import look_up_client_app_identity


async def get_client_app() -> Response:
    user_id = session.get("user_id")
    if not user_id:
        return Response("User not authenticated", status=401)

    client_id = request.args.get("clientId")
    if not client_id:
        return Response("Client ID not provided", status=400)

    client_app_info = await look_up_client_app_identity(client_id)
    if not client_app_info:
        return Response("Client app not found", status=404)

    return Response(
        json.dumps(
            {
                "clientId": client_id,
                "name": client_app_info.display_name,
                "verified": (
                    client_app_info.nip05.verification_status.value
                    if client_app_info.nip05
                    else None
                ),
                "avatar": client_app_info.image_url,
                "domain": (
                    client_app_info.nip05.domain if client_app_info.nip05 else None
                ),
            }
        )
    )
