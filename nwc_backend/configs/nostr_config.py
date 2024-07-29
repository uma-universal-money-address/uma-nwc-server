# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os
from dataclasses import dataclass

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


nostr_config: NostrConfig = NostrConfig.load()
