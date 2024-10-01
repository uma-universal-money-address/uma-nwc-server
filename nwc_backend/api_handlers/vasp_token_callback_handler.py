# pyre-strict

from urllib.parse import parse_qs, unquote, urlencode, urlparse, urlunparse
from uuid import uuid4

from quart import current_app, redirect, request, session
from werkzeug import Response as WerkzeugResponse

from nwc_backend.db import db
from nwc_backend.models.user import User
from nwc_backend.models.vasp_jwt import VaspJwt


async def handle_vasp_token_callback() -> WerkzeugResponse:
    short_lived_vasp_token = request.args.get("token")
    if not short_lived_vasp_token:
        return WerkzeugResponse("No token provided", status=400)
    vasp_jwt = VaspJwt.from_jwt(short_lived_vasp_token)

    fe_redirect_path = request.args.get("fe_redirect")
    if fe_redirect_path:
        fe_redirect_path = unquote(fe_redirect_path)
    frontend_redirect_url = current_app.config["NWC_APP_ROOT_URL"] + (
        fe_redirect_path or "/"
    )
    try:
        parsed_url = urlparse(frontend_redirect_url)
    except ValueError as e:
        return WerkzeugResponse(
            f"Invalid redirect url: {frontend_redirect_url}. {e}", status=400
        )

    query_params = parse_qs(parsed_url.query)
    query_params["token"] = short_lived_vasp_token
    query_params["uma_address"] = [vasp_jwt.uma_address]
    query_params["expiry"] = [vasp_jwt.expiry]
    query_params["currency"] = request.args.get("currency")
    parsed_url = parsed_url._replace(query=urlencode(query_params, doseq=True))
    frontend_redirect_url = str(urlunparse(parsed_url))

    if not short_lived_vasp_token:
        return WerkzeugResponse("No token provided", status=400)

    # TODO: Add middleware to handle authed requests instead of relying on user_id in session
    user = await User.from_vasp_user_id(vasp_jwt.user_id)
    if not user:
        user = User(
            id=uuid4(),
            vasp_user_id=vasp_jwt.user_id,
            uma_address=vasp_jwt.uma_address,
        )
        db.session.add(user)
        await db.session.commit()
    session["user_id"] = user.id

    return redirect(frontend_redirect_url)
