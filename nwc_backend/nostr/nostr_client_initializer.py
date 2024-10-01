# pyre-strict

import asyncio
import logging

from nostr_sdk import Event, Filter, HandleNotification, Kind, KindEnum, RelayMessage
from quart import current_app

from nwc_backend.event_handlers.event_builder import EventBuilder
from nwc_backend.event_handlers.nip47_event_handler import handle_nip47_event
from nwc_backend.exceptions import PublishEventFailedException
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.nostr.nostr_client import nostr_client
from nwc_backend.nostr.nostr_config import NostrConfig


class NotificationHandler(HandleNotification):
    async def handle(self, relay_url: str, subscription_id: str, event: Event) -> None:
        async with current_app.app_context():
            logging.info("Received new event from %s: %s", relay_url, event.as_json())

            match event.kind().as_enum():
                case KindEnum.WALLET_CONNECT_REQUEST():
                    await handle_nip47_event(event)
                case _:
                    raise NotImplementedError()

    async def handle_msg(self, relay_url: str, msg: RelayMessage) -> None:
        logging.info("Received new message from %s: %s", relay_url, msg.as_json())


async def init_nostr_client() -> None:
    nostr_config = NostrConfig.instance()
    await nostr_client.add_relay(nostr_config.relay_url)
    await nostr_client.connect()

    try:
        await _publish_nip47_info()
    except Exception:
        logging.exception("Failed to publish nip47.")

    nip47_filter = (
        Filter()
        .pubkey(nostr_config.identity_keys.public_key())
        .kind(Kind.from_enum(KindEnum.WALLET_CONNECT_REQUEST()))  # pyre-ignore[6]
    )
    await nostr_client.subscribe([nip47_filter])
    asyncio.create_task(nostr_client.handle_notifications(NotificationHandler()))


async def _publish_nip47_info() -> None:
    nip47_info_event = EventBuilder(
        kind=KindEnum.WALLET_CONNECT_INFO(),  # pyre-ignore[6]
        content=" ".join([method.value for method in list(Nip47RequestMethod)]),
    ).build()
    response = await nostr_client.send_event(nip47_info_event)

    logging.debug(
        "Nip47 info published %s: success %s, failed %s",
        response.id.to_hex(),
        str(response.output.success),
        str(response.output.failed),
    )

    if not response.output.success:
        raise PublishEventFailedException(nip47_info_event, response.output.failed)
