# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from nwc_backend.models.model_base import ModelBase
from sqlalchemy import String, Integer, ForeignKey, Text, TIMESTAMP
import json
from nwc_backend.event_handlers.nip47_request_method import Nip47RequestMethod
from nwc_backend.db import Column


class AppConnection(ModelBase):
    __tablename__ = "app_connection"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    app_name = Column(String(255))
    description = Column(String(255))
    nostr_pubkey = Column(String(255))
    required_commands = Column(Text)  # Store JSON as string
    optional_commands = Column(Text)  # Store JSON as string
    max_budget_per_month = Column(Integer)
    expires_at = Column(TIMESTAMP(timezone=True))
    long_lived_vasp_token = Column(String(255))

    def set_required_commands(self, commands: list[Nip47RequestMethod]) -> None:
        commands_vals = [command.value for command in commands]
        self.required_commands = json.dumps(commands_vals)

    def get_required_commands(self) -> list[Nip47RequestMethod]:
        command_vals = json.loads(self.required_commands)
        return [Nip47RequestMethod(command) for command in command_vals]

    def set_optional_commands(self, commands: list[Nip47RequestMethod]) -> None:
        commands_vals = [command.value for command in commands]
        self.optional_commands = json.dumps(commands_vals)

    def get_optional_commands(self) -> list[Nip47RequestMethod]:
        command_vals = json.loads(self.optional_commands)
        return [Nip47RequestMethod(command) for command in command_vals]
