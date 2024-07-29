# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from datetime import datetime, timezone
from hashlib import sha256

from nostr_sdk import Event, Keys, Kind, KindEnum

from nwc_backend.configs.nostr_config import nostr_config


class EventBuilder:
    def __init__(self, kind: KindEnum, content: str) -> None:
        self.kind: Kind = Kind.from_enum(kind)
        self.content = content
        self.created_at = int(datetime.now(timezone.utc).timestamp())
        self.tags: list[list[str]] = []

    def add_tag(self, tag: list[str]) -> "EventBuilder":
        self.tags.append(tag)
        return self

    def build(self) -> Event:
        event_id = self._compute_id()
        signature = self._sign(event_id)
        return Event.from_json(
            json.dumps(
                {
                    "id": event_id,
                    "pubkey": nostr_config.identity_pubkey.to_hex(),
                    "created_at": self.created_at,
                    "kind": self.kind.as_u16(),
                    "tags": self.tags,
                    "content": self.content,
                    "sig": signature,
                }
            )
        )

    def _compute_id(self) -> str:
        data = [
            0,
            nostr_config.identity_pubkey,
            self.created_at,
            self.kind.as_u16(),
            self.tags,
            self.content,
        ]
        serialized_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return sha256(serialized_data.encode()).hexdigest()

    def _sign(self, message: str) -> str:
        keys = Keys.parse(nostr_config.identity_privkey.to_hex())
        return keys.sign_schnorr(bytes.fromhex(message))
