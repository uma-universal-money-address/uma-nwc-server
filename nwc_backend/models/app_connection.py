# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, select
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

    nostr_pubkey: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    nwc_connection_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("nwc_connection.id"), nullable=False
    )
    access_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), index=True)
    connection_expiration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    nwc_connection: Mapped[NWCConnection] = relationship("NWCConnection")

    @staticmethod
    async def from_nostr_pubkey(nostr_pubkey: str) -> Optional["AppConnection"]:
        with Session(db.engine) as db_session:
            query = select(AppConnection).filter_by(nostr_pubkey=nostr_pubkey)
            return db_session.scalar(query)

    def get_expires_at(self) -> datetime:
        return (
            self.connection_expiration.replace(tzinfo=timezone.utc)
            if not self.connection_expiration.tzinfo
            else self.connection_expiration
        )

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        return self.nwc_connection.has_command_permission(command)

    def is_expired(self) -> bool:
        return self.connection_expiration < datetime.now(tz=timezone.utc)
