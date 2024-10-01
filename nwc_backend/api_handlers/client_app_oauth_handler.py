# pyre-strict

import json
import logging
from time import time
from typing import Any
from urllib.parse import unquote, urlencode
from uuid import uuid4

from aioauth.utils import create_s256_code_challenge
from quart import Response, current_app, redirect, request, session
from quart_cors import route_cors
from werkzeug import Response as WerkzeugResponse

from nwc_backend.db import db
from nwc_backend.exceptions import InvalidApiParamsException
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import (
    METHOD_TO_PERMISSIONS_GROUP,
    PermissionsGroup,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.user import User
from nwc_backend.models.vasp_jwt import VaspJwt
from nwc_backend.nostr.client_app_identity_lookup import look_up_client_app_identity
from nwc_backend.typing import none_throws


async def handle_oauth_request() -> Response | WerkzeugResponse:
    short_lived_vasp_token = request.args.get("token")
    try:
        if not short_lived_vasp_token:
            return await _handle_client_app_oauth_request()
        # if short_lived_jwt is present, means user has logged in and this is redirect  from VASP to frontend, and frontend is making this call
        return await _handle_vasp_oauth_callback(short_lived_vasp_token)
    except InvalidApiParamsException as ex:
        return Response(ex.message, status=400)


async def _handle_client_app_oauth_request() -> Response | WerkzeugResponse:
    # check no missing mandatory fields
    client_id = _require_string_param(request.args, "client_id")
    _require_string_param(request.args, "required_commands")
    code_challenge_method = _require_string_param(request.args, "code_challenge_method")
    if code_challenge_method != "S256":
        return Response("Only S256 code challenge method is supported", status=400)
    _require_string_param(request.args, "code_challenge")
    redirect_uri = _require_string_param(request.args, "redirect_uri")

    budget = request.args.get("budget")
    if budget:
        budget = unquote(budget)
        if not SpendingLimit.is_budget_valid(budget):
            return Response(
                "Budget should be in the format <max_amount>.<currency>/<period>",
                status=400,
            )

    client_app_info = await look_up_client_app_identity(client_id)
    if not client_app_info:
        logging.error(
            "Received an empty response for client app identity lookup for client_id %s",
            client_id,
        )
        # TODO: Sync with @brian on how we want to handle this
        return Response("Client app not found", status=404)

    if not client_app_info.is_redirect_url_allowed(redirect_uri):
        return Response("Redirect url not allowed", status=403)

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
    await db.session.commit()
    session["client_app_id"] = client_app.id

    uma_vasp_login_url = current_app.config["UMA_VASP_LOGIN_URL"]
    # redirect back to the same url with the short lived jwt added
    request_params = request.query_string.decode()
    query_params = urlencode(
        {
            "redirect_uri": current_app.config["NWC_APP_ROOT_URL"]
            + "/oauth/auth"
            + "?"
            + request_params,
        }
    )
    vasp_url_with_query = (
        uma_vasp_login_url + "?" + query_params
        if "?" not in uma_vasp_login_url
        else uma_vasp_login_url + "&" + query_params
    )
    logging.debug("REDIRECT to %s", vasp_url_with_query)
    return redirect(vasp_url_with_query)


async def _handle_vasp_oauth_callback(
    short_lived_vasp_token: str,
) -> Response | WerkzeugResponse:
    vasp_jwt = VaspJwt.from_jwt(short_lived_vasp_token)
    vasp_supported_commands = current_app.config.get("VASP_SUPPORTED_COMMANDS")
    required_permissions_groups: set[PermissionsGroup] = set()
    for command in request.args["required_commands"].split():
        if command not in vasp_supported_commands:
            return Response(
                f"Command {command} is not supported by the NWC",
                status=400,
            )
        required_permissions_groups.add(METHOD_TO_PERMISSIONS_GROUP[command])

    optional_permissions_groups: set[PermissionsGroup] = set()
    optional_commands = request.args.get("optional_commands")
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
        await db.session.commit()

    session["redirect_uri"] = request.args["redirect_uri"]
    session["user_id"] = user.id
    session["client_state"] = request.args.get("state")
    session["short_lived_vasp_token"] = short_lived_vasp_token
    session["code_challenge"] = request.args["code_challenge"]

    # REMOVE ALWAYS_GRANTED PermissionsGroup from lists if it exists since we won't be sending them to the frontend
    required_permissions_groups.discard(PermissionsGroup.ALWAYS_GRANTED)
    optional_permissions_groups.discard(PermissionsGroup.ALWAYS_GRANTED)

    nwc_frontend_new_app = current_app.config["NWC_APP_ROOT_URL"] + "/apps/new"
    query_params = {
        "client_id": request.args["client_id"],
        "optional_commands": ",".join([c.value for c in optional_permissions_groups]),
        "required_commands": ",".join([c.value for c in required_permissions_groups]),
        "token": short_lived_vasp_token,
        "uma_address": vasp_jwt.uma_address,
        "redirect_uri": request.args["redirect_uri"],
        "expiry": vasp_jwt.expiry,
    }
    if "budget" in request.args:
        query_params["budget"] = request.args["budget"]
    if "currency" in request.args:
        query_params["currency"] = request.args["currency"]
    nwc_frontend_new_app = nwc_frontend_new_app + "?" + urlencode(query_params)
    return redirect(nwc_frontend_new_app)


@route_cors(  # pyre-ignore[56]
    allow_origin=["*"],
    allow_headers=[
        "Authorization",
        "X-User-Agent",
    ],
)
async def handle_token_exchange() -> Response:
    # Default to post body. Fall back to query params if post body is empty.
    request_data = await request.form
    if not request_data:
        request_data = request.args

    grant_type = request_data.get("grant_type")
    try:
        if grant_type == "authorization_code":
            return await _exchange_token(request_data)
        elif grant_type == "refresh_token":
            return await _refresh_token(request_data)
        else:
            return Response("Invalid grant type", status=400)
    except InvalidApiParamsException as ex:
        return Response(ex.message, status=400)


async def _exchange_token(request_data: dict[str, Any]) -> Response:
    client_id = _require_string_param(request_data, "client_id")
    code = _require_string_param(request_data, "code")
    redirect_uri = _require_string_param(request_data, "redirect_uri")
    code_verifier = _require_string_param(request_data, "code_verifier")

    nwc_connection = await NWCConnection.from_oauth_authorization_code(code)
    if (
        not nwc_connection
        or not nwc_connection.client_app
        or nwc_connection.client_app.client_id != client_id
    ):
        return Response("Invalid authorization code", status=401)

    redirect_without_params = redirect_uri.split("?")[0]
    connection_redirect_without_params = (
        nwc_connection.redirect_uri.split("?")[0]
        if nwc_connection.redirect_uri
        else None
    )
    if redirect_without_params != connection_redirect_without_params:
        return Response("Redirect URI mismatch", status=401)

    computed_code_challenge = create_s256_code_challenge(code_verifier)
    if nwc_connection.code_challenge != computed_code_challenge:
        return Response("Code challenge mismatch", status=401)

    response = await nwc_connection.refresh_oauth_tokens()
    return Response(
        json.dumps(response),
        status=200,
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        },
    )


async def _refresh_token(request_data: dict[str, Any]) -> Response:
    refresh_token = _require_string_param(request_data, "refresh_token")
    client_id = _require_string_param(request_data, "client_id")
    nwc_connection = await NWCConnection.from_oauth_refresh_token(refresh_token)
    if (
        not nwc_connection
        or not nwc_connection.client_app
        or nwc_connection.client_app.client_id != client_id
    ):
        return Response("Invalid refresh token", status=401)

    if none_throws(nwc_connection.refresh_token_expires_at) < int(time()):
        return Response("Refresh token expired", status=401)

    if nwc_connection.is_connection_expired():
        return Response("Connection expired", status=401)

    response = await nwc_connection.refresh_oauth_tokens()
    return Response(
        json.dumps(response),
        status=200,
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        },
    )


def _require_string_param(dict: dict[str, Any], param: str) -> str:
    value = dict.get(param)
    if not value:
        raise InvalidApiParamsException(f"Missing required parameter: {param}")
    if not isinstance(value, str):
        raise InvalidApiParamsException(
            f"Invalid type for parameter {param}: {type(value)}"
        )
    return value
