# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from datetime import datetime, timezone
from urllib.parse import urlencode
from uuid import uuid4

from quart import Quart, redirect, request, session
from werkzeug import Response as WerkzeugResponse

from nwc_backend.client_app_identity_lookup import look_up_client_app_identity
from nwc_backend.db import db
from nwc_backend.exceptions import InvalidBudgetFormatException
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import (
    METHOD_TO_PERMISSIONS_GROUP,
    PermissionsGroup,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.user import User
from nwc_backend.models.vasp_jwt import VaspJwt


async def handle_vasp_oauth_callback(app: Quart) -> WerkzeugResponse:
    short_lived_vasp_token = request.args.get("token")

    required_commands = request.args.get("required_commands")
    if not required_commands:
        return WerkzeugResponse("Required commands not provided", status=400)
    optional_commands = request.args.get("optional_commands")
    client_id = request.args.get("client_id")
    code_challenge_method = request.args.get("code_challenge_method")
    if code_challenge_method != "S256":
        return WerkzeugResponse(
            "Only S256 code challenge method is supported", status=400
        )
    redirect_uri = request.args.get("redirect_uri")
    code_challenge = request.args.get("code_challenge")
    if not code_challenge:
        return WerkzeugResponse("Code challenge not provided", status=400)
    if not redirect_uri:
        return WerkzeugResponse("Redirect URI not provided", status=400)

    now = datetime.now(timezone.utc)
    budget = request.args.get("budget")
    spending_limit = None
    if budget:
        try:
            spending_limit = SpendingLimit.from_budget_repr(
                budget=budget, start_time=now
            )
        except InvalidBudgetFormatException as ex:
            return WerkzeugResponse(
                ex.error_message,
                status=400,
            )

    vasp_jwt = VaspJwt.from_jwt(short_lived_vasp_token)

    vasp_supported_commands = app.config.get("VASP_SUPPORTED_COMMANDS")
    required_permissions_groups: set[PermissionsGroup] = set()
    for command in required_commands.split():
        if command not in vasp_supported_commands:
            return WerkzeugResponse(
                f"Command {command} is not supported by the NWC",
                status=400,
            )
        required_permissions_groups.add(METHOD_TO_PERMISSIONS_GROUP[command])

    optional_permissions_groups: set[PermissionsGroup] = set()
    if optional_commands:
        optional_commands = optional_commands.split()
        for command in optional_commands:
            if command not in vasp_supported_commands:
                continue
            group = METHOD_TO_PERMISSIONS_GROUP[command]
            optional_permissions_groups.add(group)
    granted_permissions_groups = required_permissions_groups.union(
        optional_permissions_groups
    )
    granted_permissions_groups.add(PermissionsGroup.ALWAYS_GRANTED)

    user = await User.from_vasp_user_id(vasp_jwt.user_id)
    if not user:
        user = User(
            id=uuid4(),
            vasp_user_id=vasp_jwt.user_id,
            uma_address=vasp_jwt.uma_address,
        )
        db.session.add(user)

    client_app_info = await look_up_client_app_identity(client_id)
    if not client_app_info:
        logging.error(
            "Received an empty response for client app identity lookup for client_id %s",
            client_id,
        )
        # TODO: Sync with @brian on how we want to handle this
        return WerkzeugResponse("Client app not found", status=404)

    if not client_app_info.is_redirect_url_allowed(redirect_uri):
        return WerkzeugResponse("Redirect url not allowed", status=403)

    client_app = await ClientApp.from_client_id(client_id)
    if client_app:
        client_app.app_name = client_app_info.name
        client_app.display_name = client_app_info.display_name
        client_app.verification_status = (
            client_app_info.nip05.verification_status if client_app_info.nip05 else None
        )
        client_app.image_url = client_app_info.image_url
    else:
        client_app = ClientApp(
            id=uuid4(),
            client_id=client_id,
            app_name=client_app_info.name,
            display_name=client_app_info.display_name,
            verification_status=(
                client_app_info.nip05.verification_status
                if client_app_info.nip05
                else None
            ),
            image_url=client_app_info.image_url,
        )
        db.session.add(client_app)

    nwc_connection = NWCConnection(
        id=uuid4(),
        user_id=user.id,
        client_app_id=client_app.id,
        granted_permissions_groups=[
            group.value for group in granted_permissions_groups
        ],
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
    )

    db.session.add(nwc_connection)
    await db.session.commit()

    if spending_limit:
        spending_limit.nwc_connection_id = nwc_connection.id
        nwc_connection.spending_limit_id = spending_limit.id
        db.session.add(spending_limit)
        await db.session.commit()

    session["short_lived_vasp_token"] = short_lived_vasp_token
    session["nwc_connection_id"] = nwc_connection.id
    session["user_id"] = user.id
    session["client_state"] = request.args.get("state")

    # REMOVE ALWAYS_GRANTED PermissionsGroup from lists if it exists since we won't be sending them to the frontend
    required_permissions_groups.discard(PermissionsGroup.ALWAYS_GRANTED)
    optional_permissions_groups.discard(PermissionsGroup.ALWAYS_GRANTED)

    nwc_frontend_new_app = app.config["NWC_APP_ROOT_URL"] + "/apps/new"
    query_params = {
        "client_id": client_id,
        "optional_commands": ",".join([c.value for c in optional_permissions_groups]),
        "required_commands": ",".join([c.value for c in required_permissions_groups]),
        "token": short_lived_vasp_token,
        "budget": budget,
        "uma_address": vasp_jwt.uma_address,
        "redirect_uri": request.args.get("redirect_uri"),
        "expiry": vasp_jwt.expiry,
        "currency": request.args.get("currency"),
    }
    nwc_frontend_new_app = nwc_frontend_new_app + "?" + urlencode(query_params)
    return redirect(nwc_frontend_new_app)
