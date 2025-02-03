import jwt
from quart import current_app


class VaspJwt:
    def __init__(self, user_id: str, uma_address: str, expiry: int):
        self.user_id = user_id
        self.uma_address = uma_address
        self.expiry = expiry

    @staticmethod
    def from_jwt(jwt_str: str) -> "VaspJwt":
        iss = current_app.config.get("UMA_VASP_JWT_ISS")
        aud = current_app.config.get("UMA_VASP_JWT_AUD")
        vasp_token_payload = jwt.decode(
            jwt_str,
            current_app.config.get("UMA_VASP_JWT_PUBKEY"),
            algorithms=["ES256"],
            options={"verify_aud": aud is not None, "verify_iss": iss is not None},
            audience=aud,
            issuer=iss,
        )
        return VaspJwt(
            user_id=vasp_token_payload["sub"],
            uma_address=vasp_token_payload["address"],
            expiry=vasp_token_payload["exp"],
        )
