# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import db
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection


class AppConnection(ModelBase):
    """
    Represents a connection to the NWC server and the client app.
    """

    __tablename__ = "app_connection"

    client_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("user.id"), nullable=False
    )
    nwc_connection_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("nwc_connection.id"), nullable=False
    )
    nostr_pubkey: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
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
    revoked: Mapped[bool] = mapped_column(Boolean(), default=False)

    nwc_connection: Mapped[NWCConnection] = relationship("NWCConnection")

    @staticmethod
    def from_nostr_pubkey(nostr_pubkey: str) -> Optional["AppConnection"]:
        with Session(db.engine) as db_session:
            return (
                db_session.query(AppConnection)
                .filter_by(nostr_pubkey=nostr_pubkey)
                .first()
            )

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        return self.nwc_connection.has_command_permission(command)

    def is_access_token_expired(self) -> bool:
        return datetime.now(timezone.utc).timestamp() >= self.access_token_expires_at
