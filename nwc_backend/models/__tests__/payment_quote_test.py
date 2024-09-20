# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from secrets import token_hex
from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_nip47_request
from nwc_backend.models.payment_quote import PaymentQuote


async def test_payment_quote(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        nip47_request = await create_nip47_request()
        payment_hash = token_hex()
        amount = 100
        currency_code = "USD"
        quote = PaymentQuote(
            id=uuid4(),
            nip47_request_id=nip47_request.id,
            payment_hash=payment_hash,
            sending_currency_code=currency_code,
            sending_currency_amount=amount,
        )
        db.session.add(quote)
        await db.session.commit()

        quote = await PaymentQuote.from_payment_hash(payment_hash)
        assert quote
        assert quote.nip47_request_id == nip47_request.id
        assert quote.sending_currency_amount == amount
        assert quote.sending_currency_code == currency_code

        assert not await PaymentQuote.from_payment_hash("abcde")
