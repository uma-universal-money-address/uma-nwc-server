# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from nwc_backend.client_app_identity_lookup import Nip05VerificationStatus
from nwc_backend.models.model_base import ModelBase
from sqlalchemy import Enum as DBEnum


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
