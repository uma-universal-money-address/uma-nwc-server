# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Optional

from nostr_sdk import Event, Keys, Kind, KindEnum, Nip47Error, PublicKey, nip04_encrypt

from nwc_backend.configs.nostr_config import NostrConfig
from nwc_backend.exceptions import EventBuilderException
from nwc_backend.models.nip47_request_method import Nip47RequestMethod


class EventBuilder:
    def __init__(self, kind: KindEnum, content: str) -> None:
        self.kind: Kind = Kind.from_enum(kind)
        self.content = content
        self.created_at = int(datetime.now(timezone.utc).timestamp())
        self.tags: list[list[str]] = []
        self.content_encrypted = False

    def add_tag(self, tag: list[str]) -> "EventBuilder":
        self.tags.append(tag)
        return self

    def encrypt_content(self, recipient_pubkey: PublicKey) -> "EventBuilder":
        if self.content_encrypted:
            raise EventBuilderException("Content has already been encrypted.")

        self.content = nip04_encrypt(
            secret_key=NostrConfig.instance().identity_privkey,
            public_key=recipient_pubkey,
            content=self.content,
        )
        self.content_encrypted = True
        return self

    def build(self) -> Event:
        if (
            self.kind.as_enum()
            in (KindEnum.WALLET_CONNECT_REQUEST(), KindEnum.WALLET_CONNECT_RESPONSE())
            and not self.content_encrypted
        ):
            raise EventBuilderException(
                "Content must be encrypted using nip04 for nip47 request and response."
            )

        event_id = self._compute_id()
        signature = self._sign(event_id)
        return Event.from_json(
            json.dumps(
                {
                    "id": event_id,
                    "pubkey": NostrConfig.instance().identity_pubkey.to_hex(),
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
            NostrConfig.instance().identity_pubkey.to_hex(),
            self.created_at,
            self.kind.as_u16(),
            self.tags,
            self.content,
        ]
        serialized_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return sha256(serialized_data.encode()).hexdigest()

    def _sign(self, message: str) -> str:
        keys = Keys.parse(NostrConfig.instance().identity_privkey.to_hex())
        return keys.sign_schnorr(bytes.fromhex(message))


def create_nip47_response(
    event: Event, method: Nip47RequestMethod, result: dict[str, Any]
) -> Event:
    content = {"result_type": method.value, "result": result}
    return (
        EventBuilder(
            kind=KindEnum.WALLET_CONNECT_RESPONSE(),  # pyre-ignore[6]
            content=json.dumps(content),
        )
        .encrypt_content(event.author())
        .add_tag(["p", NostrConfig.instance().identity_pubkey.to_hex()])
        .add_tag(["e", event.id().to_hex()])
        .build()
    )


def create_nip47_error_response(
    event: Event, method: Optional[Nip47RequestMethod], error: Nip47Error
) -> Event:
    content = {
        "error": {"code": error.code.name, "message": error.message},
    }
    if method:
        content["result_type"] = method.value

    return (
        EventBuilder(
            kind=KindEnum.WALLET_CONNECT_RESPONSE(),  # pyre-ignore[6]
            content=json.dumps(content),
        )
        .encrypt_content(event.author())
        .add_tag(["p", NostrConfig.instance().identity_pubkey.to_hex()])
        .add_tag(["e", event.id().to_hex()])
        .build()
    )
