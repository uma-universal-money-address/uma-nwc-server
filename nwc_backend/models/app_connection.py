# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Text, select
from sqlalchemy.orm import Session

from nwc_backend.db import Column, db
from nwc_backend.event_handlers.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.model_base import ModelBase
from nwc_backend.typing import none_throws


class AppConnection(ModelBase):
    __tablename__ = "app_connection"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    app_name = Column(String(255))
    description = Column(String(255))
    nostr_pubkey = Column(String(255), unique=True)
    supported_commands = Column(Text)  # Store JSON as string
    max_budget_per_month = Column(Integer)
    expires_at = Column(TIMESTAMP(timezone=True))
    long_lived_vasp_token = Column(String(255))

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
