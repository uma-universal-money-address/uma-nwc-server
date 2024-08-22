# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from dataclasses import dataclass
from typing import Optional

from nostr_sdk import Keys, PublicKey, SecretKey
from quart import Quart, current_app


@dataclass
class NostrConfig:
    relay_url: str
    identity_privkey: SecretKey
    identity_pubkey: PublicKey

    @staticmethod
    def load(app: Optional[Quart] = None) -> "NostrConfig":
        if app is None:
            app = current_app
        keys = Keys.parse(app.config["NOSTR_PRIVKEY"])
        return NostrConfig(
            relay_url=app.config["RELAY"],
            identity_privkey=keys.secret_key(),
            identity_pubkey=keys.public_key(),
        )

    @staticmethod
    def instance(app: Optional[Quart] = None) -> "NostrConfig":
        global _nostr_config  # noqa: PLW0603
        if _nostr_config is None:
            _nostr_config = NostrConfig.load(app)

        return _nostr_config


_nostr_config: Optional[NostrConfig] = None
