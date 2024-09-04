# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, BigInteger
from sqlalchemy import Enum as DBEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nwc_backend.db import UUID as DBUUID
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.spending_limit_frequency import SpendingLimitFrequency
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
    long_lived_vasp_token: Mapped[Optional[str]] = mapped_column(String(1024))
    connection_expires_at: Mapped[Optional[int]] = mapped_column(Integer())
    spending_limit_amount: Mapped[Optional[int]] = mapped_column(BigInteger())
    spending_limit_currency_code: Mapped[Optional[str]] = mapped_column(String(3))
    spending_limit_frequency: Mapped[Optional[SpendingLimitFrequency]] = mapped_column(
        DBEnum(SpendingLimitFrequency, native_enum=False)
    )

    user: Mapped[User] = relationship("User", lazy="joined")
    client_app: Mapped[ClientApp] = relationship("ClientApp", lazy="joined")

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        return command.value in self.supported_commands
