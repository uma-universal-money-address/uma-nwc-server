# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging

from nostr_sdk import Event, HandleNotification, KindEnum, RelayMessage

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
