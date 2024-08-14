# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os
from dataclasses import dataclass
from typing import Optional

from nostr_sdk import Keys, PublicKey, SecretKey


@dataclass
class NostrConfig:
    relay_url: str
    identity_privkey: SecretKey
    identity_pubkey: PublicKey

    @staticmethod
    def load() -> "NostrConfig":
        keys = Keys.parse(os.environ["NOSTR_PRIVKEY"])
        return NostrConfig(
            relay_url=os.environ["RELAY"],
            identity_privkey=keys.secret_key(),
            identity_pubkey=keys.public_key(),
        )

    @staticmethod
    def instance() -> "NostrConfig":
        global _nostr_config  # noqa: PLW0603
        if _nostr_config is None:
            _nostr_config = NostrConfig.load()

        return _nostr_config


_nostr_config: Optional[NostrConfig] = None
