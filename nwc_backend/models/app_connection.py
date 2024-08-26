# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import db
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.app_connection_status import AppConnectionStatus
from sqlalchemy import Enum as DBEnum
from sqlalchemy import Index


class AppConnection(ModelBase):
    """
    Represents a connection to the NWC server and the client app.
    """

    __tablename__ = "app_connection"

    nwc_connection_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("nwc_connection.id"), nullable=False
    )
    nostr_pubkey: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    access_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    authorization_code: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    # Expiration times for the tokens are stored as Unix timestamps
    access_token_expires_at: Mapped[int] = mapped_column(Integer(), nullable=False)
    refresh_token_expires_at: Mapped[int] = mapped_column(Integer(), nullable=False)
    authorization_code_expires_at: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
    )
    status: Mapped[AppConnectionStatus] = mapped_column(
        DBEnum(AppConnectionStatus, native_enum=False),
        nullable=False,
    )

    nwc_connection: Mapped[NWCConnection] = relationship("NWCConnection")

    @staticmethod
    def from_nostr_pubkey(nostr_pubkey: str) -> Optional["AppConnection"]:
        return (
            db.session.query(AppConnection).filter_by(nostr_pubkey=nostr_pubkey).first()
        )

    async def get_client_app(self) -> ClientApp:
        with Session(db.engine) as db_session:
            client_app = db_session.get(ClientApp, self.nwc_connection.client_app_id)
            return client_app

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        return self.nwc_connection.has_command_permission(command)

    def is_access_token_expired(self) -> bool:
        return datetime.now(timezone.utc).timestamp() >= self.access_token_expires_at

    async def get_connection_reponse_data(self) -> dict[str, Any]:
        # TODO: Address the fields that are marked as TODO
        client_app = await self.get_client_app()
        response = {
            "connectionId": self.id,
            "clientId": self.nwc_connection.client_app.client_id,
            "name": client_app.app_name,
            "createdAt": self.created_at,
            "lastUsedAt": "TODO",
            "amountInLowestDenom": "TODO",
            "amountInLowestDenomUsed": "TODO",
            "limitFrequency": "MONTHLY",
            "limitEnabled": self.nwc_connection.max_budget_per_month is not None,
            # TODO: currency should be fetched from somewhere
            "currency": {
                "code": "USD",
                "name": "US Dollar",
                "symbol": "$",
                "decimals": 2,
                "type": "fiat",
            },
            "permissions": self.nwc_connection.supported_commands,
            "avatar": client_app.image_url,
            "status": self.status.value,
        }

        return response


Index(
    "app_connection_nwc_connection_unique_idx",
    AppConnection.nwc_connection_id,
    unique=True,
    postgresql_where=AppConnection.status == AppConnectionStatus.ACTIVE,
    sqlite_where=AppConnection.status == AppConnectionStatus.ACTIVE,
)
