# pyre-strict

import json

from quart import Response, request

from nwc_backend.nostr.client_app_identity_lookup import look_up_client_app_identity


async def get_client_app() -> Response:
    client_id = request.args.get("clientId")
    if not client_id:
        return Response("Client ID not provided", status=400)

    client_app_info = await look_up_client_app_identity(client_id)
    if not client_app_info:
        return Response("Client app not found", status=404)

    nip68_verification_json = None
    if client_app_info.app_authority_verification:
        nip68_verification_json = {
            "authorityName": client_app_info.app_authority_verification.authority_name,
            "authorityPublicKey": client_app_info.app_authority_verification.authority_pubkey,
            "status": client_app_info.app_authority_verification.status.value,
        }

    return Response(
        json.dumps(
            {
                "clientId": client_id,
                "name": client_app_info.display_name,
                "nip05Verification": (
                    client_app_info.nip05.verification_status.value
                    if client_app_info.nip05
                    else None
                ),
                "nip68Verification": nip68_verification_json,
                "avatar": client_app_info.image_url,
                "domain": (
                    client_app_info.nip05.domain if client_app_info.nip05 else None
                ),
            }
        )
    )
