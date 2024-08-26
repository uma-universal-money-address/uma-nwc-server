from enum import Enum


class AppConnectionStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
