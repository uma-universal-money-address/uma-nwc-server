# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from uuid import uuid4

import jwt
from quart import Quart, redirect, request, session
from werkzeug import Response as WerkzeugResponse

from nwc_backend.client_app_identity_lookup import look_up_client_app_identity
from nwc_backend.db import db
from nwc_backend.exceptions import InvalidBudgetFormatException
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import (
    METHOD_TO_PERMISSIONS_GROUP,
    PERMISSIONS_GROUP_TO_METHODS,
    PermissionsGroup,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.user import User


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

    vasp_token_payload = jwt.decode(
        short_lived_vasp_token,
        app.config.get("UMA_VASP_JWT_PUBKEY"),
        algorithms=["ES256"],
        # TODO: verify the aud and iss
        options={"verify_aud": False, "verify_iss": False},
    )
    vasp_user_id = vasp_token_payload["sub"]
    uma_address = vasp_token_payload["address"]
    expiry = vasp_token_payload["exp"]

    # map the required commands to permissions group, if any command in the permissions group is not supported by VASP return error
    vasp_supported_commands = app.config.get("VASP_SUPPORTED_COMMANDS")
    required_permissions_groups = set()
    all_granted_granular_commands = set()
    for command in required_commands.split():
        if command not in Nip47RequestMethod.get_values():
            return WerkzeugResponse(
                f"Command {command} is not supported by the NWC",
                status=400,
            )
        required_permissions_groups.add(METHOD_TO_PERMISSIONS_GROUP[command])
        all_granted_granular_commands.update(
            PERMISSIONS_GROUP_TO_METHODS[METHOD_TO_PERMISSIONS_GROUP[command]]
        )

    for command in all_granted_granular_commands:
        if command not in vasp_supported_commands:
            return WerkzeugResponse(
                f"Command {command} is not supported by the VASP",
                status=400,
            )

    # map the optional commands to permissions group, if any command in the permissions group is not supported by VASP don't include in granted permission groups
    optional_permissions_groups = set()
    if optional_commands:
        optional_commands = optional_commands.split()
        for command in optional_commands:
            if command not in Nip47RequestMethod.get_values():
                return WerkzeugResponse(
                    f"Command {command} is not supported by the NWC",
                    status=400,
                )
            group = METHOD_TO_PERMISSIONS_GROUP[command]
            all_granular_permissions_in_group = PERMISSIONS_GROUP_TO_METHODS[group]
            if any(
                command not in vasp_supported_commands
                for command in all_granular_permissions_in_group
            ):
                continue
            optional_permissions_groups.add(group)
    granted_permissions_groups = required_permissions_groups.union(
        optional_permissions_groups
    )
    granted_permissions_groups.add(PermissionsGroup.ALWAYS_GRANTED)

    # save the app connection and nwc connection in the db
    user = await User.from_vasp_user_id(vasp_user_id)
    if not user:
        user = User(
            id=uuid4(),
            vasp_user_id=vasp_user_id,
            uma_address=uma_address,
        )
        db.session.add(user)

    # update client app info, or create a new one if it doesn't exist
    client_app_info = await look_up_client_app_identity(client_id)
    if not client_app_info:
        logging.error(
            "Received an empty response for client app identity lookup for client_id %s",
            client_id,
        )
        # TODO: Sync with @brian on how we want to handle this
        return WerkzeugResponse("Client app not found", status=404)

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
    # TODO: explore how to deal with expiration of the nwc connection from user input - right now defaulted at 1 year
    connection_expires_at = int((now + timedelta(days=365)).timestamp())
    nwc_connection.connection_expires_at = connection_expires_at
    db.session.add(nwc_connection)
    await db.session.commit()

    if spending_limit:
        spending_limit.nwc_connection_id = nwc_connection.id
        nwc_connection.spending_limit_id = spending_limit.id
        db.session.add(spending_limit)
        await db.session.commit()

    # TODO: Verify these are saved on nwc frontend session
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
        "uma_address": uma_address,
        "redirect_uri": request.args.get("redirect_uri"),
        "expiry": expiry,
        "currency": request.args.get("currency"),
    }
    nwc_frontend_new_app = nwc_frontend_new_app + "?" + urlencode(query_params)
    return redirect(nwc_frontend_new_app)
