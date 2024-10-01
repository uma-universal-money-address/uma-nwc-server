from functools import partial

from quart import Blueprint, request

from nwc_backend.api_handlers import client_app_lookup_handler, nwc_connection_handler
from nwc_backend.middleware import load_auth_state

bp = Blueprint("frontend_api", __name__, url_prefix="/api")

bp.add_url_rule(
    "/connection/<connection_id>",
    view_func=nwc_connection_handler.get_connection,
    methods=["GET"],
)
bp.add_url_rule(
    "/connections",
    view_func=nwc_connection_handler.get_all_connections,
    methods=["GET"],
)
bp.add_url_rule(
    "/app",
    view_func=client_app_lookup_handler.get_client_app,
    methods=["GET"],
)
bp.add_url_rule(
    "/app",
    view_func=nwc_connection_handler.create_client_app_connection,
    methods=["POST"],
)
bp.add_url_rule(
    "/connection/<connection_id>/transactions",
    view_func=nwc_connection_handler.get_all_outgoing_payments,
    methods=["GET"],
)
bp.add_url_rule(
    "/connection/manual",
    view_func=nwc_connection_handler.create_manual_connection,
    methods=["POST"],
)
bp.add_url_rule(
    "/connection/<connection_id>",
    view_func=nwc_connection_handler.update_connection,
    methods=["POST"],
)

bp.before_request(partial(load_auth_state, request))
