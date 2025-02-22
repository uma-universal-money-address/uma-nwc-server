# pyre-strict

from datetime import datetime, timezone
from hashlib import sha256
from time import time
from typing import Any, Optional
from uuid import UUID

from aioauth.utils import generate_token
from nostr_sdk import Keys
from quart import current_app
from sqlalchemy import JSON, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import select
from uma_auth.models.currency import Currency

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import DBCurrency, db
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.permissions_grouping import (
    PERMISSIONS_GROUP_TO_METHODS,
    PermissionsGroup,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.user import User
from nwc_backend.nostr.nostr_config import NostrConfig
from nwc_backend.typing import none_throws

ACCESS_TOKEN_EXPIRES_IN: int = 30 * 24 * 60 * 60
REFRESH_TOKEN_EXPIRES_IN: int = 120 * 24 * 60 * 60
AUTHORIZATION_CODE_EXPIRES_IN: int = 10 * 60


class NWCConnection(ModelBase):
    """
    Represents a connection to the NWC server and the VASP for a specific client app.
    """

    __tablename__ = "nwc_connection"

    user_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("user.id"), nullable=False
    )
    client_app_id: Mapped[Optional[UUID]] = mapped_column(
        DBUUID(), ForeignKey("client_app.id")
    )
    custom_name: Mapped[Optional[str]] = mapped_column(String(255))
    granted_permissions_groups: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), nullable=False
    )
    long_lived_vasp_token: Mapped[str] = mapped_column(String(1024), nullable=False)
    connection_expires_at: Mapped[Optional[int]] = mapped_column(Integer())
    budget_currency: Mapped[Currency] = mapped_column(DBCurrency(), nullable=False)
    spending_limit_id: Mapped[Optional[UUID]] = mapped_column(
        DBUUID(),
        ForeignKey(
            "spending_limit.id", use_alter=True, deferrable=True, initially="DEFERRED"
        ),
    )

    # These should be set as soon as the connection is confirmed by the user.
    nostr_pubkey: Mapped[Optional[str]] = mapped_column(String(255), unique=True)

    # The following fields are only for client app oauth
    hashed_refresh_token: Mapped[Optional[str]] = mapped_column(
        String(1024), unique=True
    )
    hashed_authorization_code: Mapped[Optional[str]] = mapped_column(
        String(1024), unique=True
    )
    redirect_uri: Mapped[Optional[str]] = mapped_column(String(2048))
    code_challenge: Mapped[Optional[str]] = mapped_column(String(1024))
    # Expiration times for the tokens are stored as Unix timestamps
    access_token_expires_at: Mapped[Optional[int]] = mapped_column(Integer())
    refresh_token_expires_at: Mapped[Optional[int]] = mapped_column(Integer())
    authorization_code_expires_at: Mapped[Optional[int]] = mapped_column(Integer())

    user: Mapped[User] = relationship("User", lazy="joined")
    client_app: Mapped[Optional[ClientApp]] = relationship("ClientApp", lazy="joined")
    spending_limit: Mapped[Optional[SpendingLimit]] = relationship(
        "SpendingLimit", foreign_keys=[spending_limit_id], lazy="joined"
    )

    __table_args__ = (
        CheckConstraint(
            "client_app_id IS NOT NULL OR custom_name IS NOT NULL",
            name="check_client_app_or_custom_name",
        ),
    )

    def get_all_granted_granular_permissions(self) -> list[str]:
        all_permissions = set()
        vasp_supported_commands = current_app.config.get("VASP_SUPPORTED_COMMANDS")
        for group in self.granted_permissions_groups + [
            PermissionsGroup.ALWAYS_GRANTED.value
        ]:
            all_permissions.update(
                [
                    p
                    for p in PERMISSIONS_GROUP_TO_METHODS[PermissionsGroup(group)]
                    if p in vasp_supported_commands
                ]
            )
        return list(all_permissions)

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        return command.value in self.get_all_granted_granular_permissions()

    def create_oauth_auth_code(self) -> str:
        now = int(time())
        authorization_code = generate_token()
        self.hashed_authorization_code = sha256(authorization_code.encode()).hexdigest()
        self.authorization_code_expires_at = now + AUTHORIZATION_CODE_EXPIRES_IN
        return authorization_code

    async def refresh_oauth_tokens(self) -> dict[str, Any]:
        now = int(time())
        refresh_token = generate_token()
        self.hashed_refresh_token = sha256(refresh_token.encode()).hexdigest()
        self.refresh_token_expires_at = now + REFRESH_TOKEN_EXPIRES_IN
        keypair = Keys.generate()
        self.nostr_pubkey = keypair.public_key().to_hex()
        self.access_token_expires_at = now + ACCESS_TOKEN_EXPIRES_IN
        if self.connection_expires_at:
            self.refresh_token_expires_at = min(
                self.refresh_token_expires_at,  # pyre-ignore[6]
                self.connection_expires_at,
            )
            self.access_token_expires_at = min(
                self.access_token_expires_at,  # pyre-ignore[6]
                self.connection_expires_at,  # pyre-ignore[6]
            )
        await db.session.commit()

        access_token = keypair.secret_key().to_hex()
        spending_limit = self.spending_limit
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": ACCESS_TOKEN_EXPIRES_IN,
            "token_type": "Bearer",
            "nwc_connection_uri": self.get_nwc_connection_uri(access_token),
            "budget": (
                await spending_limit.get_budget_repr() if spending_limit else None
            ),
            "commands": self.get_all_granted_granular_permissions(),
            "nwc_expires_at": self.connection_expires_at,
            "uma_address": self.user.uma_address,
        }

    def get_nwc_connection_uri(self, access_token: str) -> str:
        nostr_config = NostrConfig.instance()
        wallet_pubkey = nostr_config.identity_keys.public_key().to_hex()
        wallet_relay = nostr_config.relay_url
        return f"nostr+walletconnect://{wallet_pubkey}?relay={wallet_relay}&lud16={self.user.uma_address}&secret={access_token}"

    @staticmethod
    async def from_nostr_pubkey(nostr_pubkey: str) -> Optional["NWCConnection"]:
        result = await db.session.execute(
            select(NWCConnection).filter_by(nostr_pubkey=nostr_pubkey)
        )
        return result.scalars().one_or_none()

    @staticmethod
    async def from_oauth_authorization_code(
        authorization_code: str,
    ) -> Optional["NWCConnection"]:
        hashed_authorization_code = sha256(authorization_code.encode()).hexdigest()
        result = await db.session.execute(
            select(NWCConnection).filter_by(
                hashed_authorization_code=hashed_authorization_code
            )
        )
        return result.scalars().one_or_none()

    @staticmethod
    async def from_oauth_refresh_token(
        refresh_token: str,
    ) -> Optional["NWCConnection"]:
        hashed_refresh_token = sha256(refresh_token.encode()).hexdigest()
        result = await db.session.execute(
            select(NWCConnection).filter_by(hashed_refresh_token=hashed_refresh_token)
        )
        return result.scalars().one_or_none()

    def is_connection_expired(self) -> bool:
        connection_expires_at = self.connection_expires_at
        if connection_expires_at and time() >= connection_expires_at:
            return True
        return False

    def is_oauth_access_token_expired(self) -> bool:
        access_token_expires_at = self.access_token_expires_at
        if access_token_expires_at and time() >= access_token_expires_at:
            return True

        return self.is_connection_expired()

    async def to_dict(self) -> dict[str, Any]:
        connection_name = (
            self.custom_name
            if self.custom_name is not None
            else none_throws(self.client_app).app_name
        )
        from nwc_backend.models.nip47_request import Nip47Request

        last_request_time = await db.session.scalar(
            select(Nip47Request.created_at)
            .filter_by(nwc_connection_id=self.id)
            .order_by(Nip47Request.created_at.desc())
            .limit(1)
        )
        response = {
            "connection_id": str(self.id),
            "client_app": self.client_app.to_dict() if self.client_app else None,
            "name": connection_name,
            "created_at": self.created_at.isoformat(),
            "last_used_at": (
                last_request_time.isoformat()
                if last_request_time
                else self.updated_at.isoformat()
            ),
            "expires_at": (
                datetime.fromtimestamp(
                    float(self.connection_expires_at), timezone.utc
                ).isoformat()
                if self.connection_expires_at
                else None
            ),
            "permissions": self.granted_permissions_groups,
            "budget_currency": self.budget_currency.to_dict(),
            "spending_limit": (
                await self.spending_limit.to_dict() if self.spending_limit else None
            ),
        }

        return response
