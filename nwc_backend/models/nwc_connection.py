# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved


import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nwc_backend.db import UUID as DBUUID
from nwc_backend.event_handlers.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.user import User


class NWCConnection(ModelBase):
    """
    Represents a connection to the NWC server and the VASP for a specific client app.
    """

    __tablename__ = "nwc_connection"

    user_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("user.id"), nullable=False
    )
    app_name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    supported_commands: Mapped[str] = mapped_column(  # Store JSON as string
        Text(), nullable=False
    )
    connection_expiration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    max_budget_per_month: Mapped[Optional[int]] = mapped_column(Integer())
    long_lived_vasp_token: Mapped[str] = mapped_column(String(255), nullable=True)
    long_lived_vasp_token_expiration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship("User")

    def set_supported_commands(self, commands: list[Nip47RequestMethod]) -> None:
        commands_vals = [command.value for command in commands]
        self.supported_commands = json.dumps(commands_vals)

    def get_supported_commands(self) -> list[Nip47RequestMethod]:
        command_vals = json.loads(self.supported_commands)
        return [Nip47RequestMethod(command) for command in command_vals]

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        command_vals = json.loads(self.supported_commands)
        return command in [Nip47RequestMethod(command) for command in command_vals]
