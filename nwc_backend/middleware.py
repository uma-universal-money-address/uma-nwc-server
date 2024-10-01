import time

from quart import abort

from nwc_backend.auth import AuthState
from nwc_backend.models.user import User
from nwc_backend.models.vasp_jwt import VaspJwt
from nwc_backend.wrappers import UmaAuthRequest


async def load_auth_state(request: UmaAuthRequest):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        abort(401, description="Unauthorized")
    short_lived_vasp_token = bearer_token.split("Bearer ")[-1]
    vasp_jwt = VaspJwt.from_jwt(short_lived_vasp_token)
    if vasp_jwt.expiry < int(time.time()):
        abort(401, description="Unauthorized")

    user = await User.from_vasp_user_id(vasp_jwt.user_id)
    if not user:
        abort(401, description="Unauthorized")

    request.auth_state = AuthState(
        user=user, expires_at=vasp_jwt.expiry, token=short_lived_vasp_token
    )
