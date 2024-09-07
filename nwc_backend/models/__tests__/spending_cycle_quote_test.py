# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from secrets import token_hex
from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_nip47_request
from nwc_backend.models.spending_cycle_quote import SpendingCycleQuote


async def test_spending_cycle_quote(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        nip47_request = await create_nip47_request()
        payment_hash = token_hex()
        amount = 100
        currency_code = "USD"
        quote = SpendingCycleQuote(
            id=uuid4(),
            nip47_request_id=nip47_request.id,
            payment_hash=payment_hash,
            estimated_amount__amount=100,
            estimated_amount__currency=currency_code,
        )
        db.session.add(quote)
        await db.session.commit()

        quote = await SpendingCycleQuote.from_payment_hash(payment_hash)
        assert quote
        assert quote.nip47_request_id == nip47_request.id
        assert quote.estimated_amount__amount == amount
        assert quote.estimated_amount__currency == currency_code

        assert not await SpendingCycleQuote.from_payment_hash("abcde")
