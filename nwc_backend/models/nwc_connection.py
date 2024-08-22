# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nwc_backend.db import UUID as DBUUID
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.user import User


class NWCConnection(ModelBase):
    """
    Represents a connection to the NWC server and the VASP for a specific client app.
    """

    __tablename__ = "nwc_connection"

    user_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("user.id"), nullable=False
    )
    client_app_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("client_app.id"), nullable=False
    )
    supported_commands: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), nullable=False
    )
    max_budget_per_month: Mapped[Optional[int]] = mapped_column(Integer())
    long_lived_vasp_token: Mapped[Optional[str]] = mapped_column(String(255))
    connection_expires_at: Mapped[Optional[int]] = mapped_column(Integer())

    user: Mapped[User] = relationship("User")
    client_app: Mapped[ClientApp] = relationship("ClientApp")

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        return command.value in self.supported_commands
