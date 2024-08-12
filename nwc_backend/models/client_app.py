# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

import json
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from nwc_backend.models.model_base import ModelBase


class ClientApp(ModelBase):
    __tablename__ = "client_app"

    client_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    client_metadata: Mapped[str] = mapped_column(Text(), nullable=True)

    def get_client_metadata(self):
        if self.client_metadata:
            data = json.loads(self.client_metadata)
            return data
        return {}

    def set_client_metadata(self, value):
        self.client_metadata = json.dumps(value)

    @property
    def logo_uri(self):
        return self.get_client_metadata().get("logo_uri")

    def get_nostr_pubkey(self):
        return self.client_id.split()[0]

    def get_identity_relay(self):
        return self.client_id.split()[1]
