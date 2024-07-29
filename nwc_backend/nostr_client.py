# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging

from nostr_sdk import (
    Client,
    Event,
    Filter,
    HandleNotification,
    Kind,
    KindEnum,
    RelayMessage,
)

from nwc_backend.configs.nostr_config import nostr_config
from nwc_backend.event_handlers.nip47_event_handler import handle_nip47_event


class NotificationHandler(HandleNotification):
    async def handle(self, relay_url: str, subscription_id: str, event: Event) -> None:
        logging.info("Received new event from %s: %s", relay_url, event.as_json())

        match event.kind().as_enum():
            case KindEnum.WALLET_CONNECT_REQUEST():
                await handle_nip47_event(event)
            case _:
                raise NotImplementedError()

    async def handle_msg(self, relay_url: str, msg: RelayMessage) -> None:
        logging.info("Received new message from %s: %s", relay_url, msg.as_json())


async def init_nostr_client() -> Client:
    await nostr_client.add_relay(nostr_config.relay_url)
    await nostr_client.connect()

    # TODO (yunyu): //publish event with NIP-47 info

    nip47_filter = (
        Filter()
        .pubkey(nostr_config.identity_pubkey)
        .kind(Kind.from_enum(KindEnum.WALLET_CONNECT_REQUEST()))  # pyre-ignore[6]
    )

    await nostr_client.handle_notifications(NotificationHandler())
    await nostr_client.subscribe([nip47_filter])

    return nostr_client


nostr_client: Client = Client()
