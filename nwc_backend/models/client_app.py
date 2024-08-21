# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Any, Optional

from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from nwc_backend.models.model_base import ModelBase


class ClientApp(ModelBase):
    __tablename__ = "client_app"

    client_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    client_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )

    @property
    def logo_uri(self) -> Optional[str]:
        return self.client_metadata.get("logo_uri") if self.client_metadata else None

    @property
    def nostr_pubkey(self) -> str:
        return self.client_id.split()[0]

    @property
    def identity_relay(self) -> str:
        return self.client_id.split()[1]
