# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import Session

from nwc_backend.db import Column, db, UUID
from nwc_backend.event_handlers.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.model_base import ModelBase
from nwc_backend.typing import none_throws
from sqlalchemy.orm import relationship


class AppConnection(ModelBase):
    """
    Represents a connection to the NWC server and the client app.
    """

    __tablename__ = "app_connection"

    nostr_pubkey = Column(String(255), unique=True)
    nwc_connection_id = Column(UUID, ForeignKey("nwc_connection.id"))

    nwc_connection = relationship(
        "NWCConnection", back_populates="app_connection", uselist=False
    )
    user = relationship("User", back_populates="app_connections")

    def set_supported_commands(self, commands: list[Nip47RequestMethod]) -> None:
        commands_vals = [command.value for command in commands]
        self.supported_commands = json.dumps(commands_vals)

    def get_supported_commands(self) -> list[Nip47RequestMethod]:
        command_vals = json.loads(self.supported_commands)
        return [Nip47RequestMethod(command) for command in command_vals]

    def has_command_permission(self, command: Nip47RequestMethod) -> bool:
        command_vals = json.loads(self.supported_commands)
        return command in [Nip47RequestMethod(command) for command in command_vals]

    def getx_expires_at(self) -> datetime:
        if self.expires_at and not self.expires_at.tzinfo:
            return self.expires_at.replace(tzinfo=timezone.utc)

        return none_throws(self.expires_at)

    @staticmethod
    async def from_nostr_pubkey(nostr_pubkey: str) -> Optional["AppConnection"]:
        with Session(db.engine) as db_session:
            query = select(AppConnection).filter_by(nostr_pubkey=nostr_pubkey)
            return await db_session.scalar(query)
