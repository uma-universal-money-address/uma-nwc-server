import jwt
from quart import current_app


class VaspJwt:
    def __init__(self, user_id: str, uma_address: str, expiry: str):
        self.user_id = user_id
        self.uma_address = uma_address
        self.expiry = expiry

    @staticmethod
    def from_jwt(jwt_str: str) -> "VaspJwt":
        vasp_token_payload = jwt.decode(
            jwt_str,
            current_app.config.get("UMA_VASP_JWT_PUBKEY"),
            algorithms=["ES256"],
            # TODO: verify the aud and iss
            options={"verify_aud": False, "verify_iss": False},
        )
        return VaspJwt(
            user_id=vasp_token_payload["sub"],
            uma_address=vasp_token_payload["address"],
            expiry=vasp_token_payload["exp"],
        )
