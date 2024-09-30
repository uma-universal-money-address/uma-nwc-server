from typing import Optional
from quart import Request, abort

from nwc_backend.auth import AuthState


class UmaAuthRequest(Request):
    auth_state: Optional[AuthState]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_state = None


def require_auth(request: Request) -> AuthState:
    assert isinstance(
        request, UmaAuthRequest
    ), "Request is not an instance of UmaAuthRequest"
    auth_state = request.auth_state
    if not auth_state:
        abort(401, description="Unauthorized")
    return auth_state
