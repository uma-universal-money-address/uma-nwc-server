# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from time import time
from typing import Any, Optional
from uuid import UUID

from aioauth.utils import generate_token
from nostr_sdk import Keys
from sqlalchemy import JSON, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import select

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import db
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.permissions_grouping import (
    PERMISSIONS_GROUP_TO_METHODS,
    PermissionsGroup,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.user import User
from nwc_backend.nostr_config import NostrConfig
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
    long_lived_vasp_token: Mapped[Optional[str]] = mapped_column(String(1024))
    connection_expires_at: Mapped[Optional[int]] = mapped_column(Integer())
    spending_limit_id: Mapped[Optional[UUID]] = mapped_column(
        DBUUID(), ForeignKey("spending_limit.id", use_alter=True)
    )
    nostr_pubkey: Mapped[Optional[str]] = mapped_column(String(255), unique=True)

    # The following fields are only for client app oauth
    refresh_token: Mapped[Optional[str]] = mapped_column(String(1024), unique=True)
    authorization_code: Mapped[Optional[str]] = mapped_column(String(1024), unique=True)
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
        for group in self.granted_permissions_groups + [
            PermissionsGroup.ALWAYS_GRANTED.value
        ]:
            all_permissions.update(
                PERMISSIONS_GROUP_TO_METHODS[PermissionsGroup(group)]
            )
        return list(all_permissions)

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        return command.value in self.get_all_granted_granular_permissions()

    def create_oauth_auth_code(self) -> str:
        now = int(time())
        authorization_code = generate_token()
        self.authorization_code = authorization_code
        self.authorization_code_expires_at = now + AUTHORIZATION_CODE_EXPIRES_IN
        return authorization_code

    async def refresh_oauth_tokens(self) -> dict[str, Any]:
        now = int(time())
        self.refresh_token = generate_token()
        self.refresh_token_expires_at = min(
            now + REFRESH_TOKEN_EXPIRES_IN, none_throws(self.connection_expires_at)
        )
        keypair = Keys.generate()
        self.nostr_pubkey = keypair.public_key().to_hex()
        self.access_token_expires_at = min(
            now + ACCESS_TOKEN_EXPIRES_IN, none_throws(self.connection_expires_at)
        )
        await db.session.commit()

        access_token = keypair.secret_key().to_hex()
        spending_limit = self.spending_limit
        return {
            "access_token": access_token,
            "refresh_token": self.refresh_token,
            "expires_in": ACCESS_TOKEN_EXPIRES_IN,
            "token_type": "Bearer",
            "nwc_connection_uri": self._get_nwc_connection_uri(access_token),
            "budget": spending_limit.get_budget_repr() if spending_limit else None,
            "commands": self.get_all_granted_granular_permissions(),
            "nwc_expires_at": self.connection_expires_at,
            "uma_address": self.user.uma_address,
        }

    def _get_nwc_connection_uri(self, access_token: str) -> str:
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
        result = await db.session.execute(
            select(NWCConnection).filter_by(authorization_code=authorization_code)
        )
        return result.scalars().one_or_none()

    @staticmethod
    async def from_oauth_refresh_token(
        refresh_token: str,
    ) -> Optional["NWCConnection"]:
        result = await db.session.execute(
            select(NWCConnection).filter_by(refresh_token=refresh_token)
        )
        return result.scalars().one_or_none()

    def is_oauth_access_token_expired(self) -> bool:
        now = time()
        access_token_expires_at = self.access_token_expires_at
        if access_token_expires_at and now >= access_token_expires_at:
            return True

        return now >= none_throws(self.connection_expires_at)

    async def get_connection_response_data(self) -> dict[str, Any]:
        if self.client_app:
            client_app = {
                "clientId": self.client_app.client_id,
                "avatar": self.client_app.image_url,
            }
        else:
            client_app = None

        spending_limit = self.spending_limit
        connection_name = (
            self.custom_name
            if self.custom_name is not None
            else none_throws(self.client_app).app_name
        )
        response = {
            "connectionId": self.id,
            "client_app": client_app,
            "name": connection_name,
            "createdAt": self.created_at,
            "lastUsedAt": "TODO",
            "amountInLowestDenom": "TODO",
            "amountInLowestDenomUsed": "TODO",
            "limitFrequency": spending_limit.frequency if spending_limit else None,
            "limitEnabled": bool(spending_limit),
            # TODO: currency should be fetched from somewhere
            "currency": {
                "code": "USD",
                "name": "US Dollar",
                "symbol": "$",
                "decimals": 2,
                "type": "fiat",
            },
            "permissions": self.granted_permissions_groups,
        }

        return response
