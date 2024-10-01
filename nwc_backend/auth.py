from dataclasses import dataclass

from nwc_backend.models.user import User


@dataclass
class AuthState:
    user: User
    expires_at: int
    token: str
