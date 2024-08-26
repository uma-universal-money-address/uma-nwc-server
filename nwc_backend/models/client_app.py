# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Optional

from sqlalchemy import Enum as DBEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import select

from nwc_backend.client_app_identity_lookup import Nip05VerificationStatus
from nwc_backend.db import db
from nwc_backend.models.model_base import ModelBase


class ClientApp(ModelBase):
    __tablename__ = "client_app"

    client_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    app_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_status: Mapped[Optional[Nip05VerificationStatus]] = mapped_column(
        DBEnum(Nip05VerificationStatus), nullable=True
    )

    @property
    def nostr_pubkey(self) -> str:
        return self.client_id.split()[0]

    @property
    def identity_relay(self) -> str:
        return self.client_id.split()[1]

    @staticmethod
    async def from_client_id(
        client_id: str,
    ) -> Optional["ClientApp"]:
        result = await db.session.execute(
            select(ClientApp).filter_by(client_id=client_id).limit(1)
        )
        return result.scalars().first()
