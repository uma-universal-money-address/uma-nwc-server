from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import (
    create_nip47_request,
    create_spending_cycle,
)
from nwc_backend.models.outgoing_payment import (
    OutgoingPayment,
    PaymentStatus,
    ReceivingAddressType,
)


async def test_outgoing_payment(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        nip47_request = await create_nip47_request()
        spending_cycle = await create_spending_cycle()
        sending_currency_amount = 1100
        sending_currency = "USD"
        estimated_budget_amount = 100
        budget_on_hold = 110
        status = PaymentStatus.PENDING
        payment = OutgoingPayment(
            id=uuid4(),
            nip47_request_id=nip47_request.id,
            nwc_connection_id=nip47_request.nwc_connection_id,
            spending_cycle_id=spending_cycle.id,
            sending_currency_amount=sending_currency_amount,
            sending_currency_code=sending_currency,
            estimated_budget_currency_amount=estimated_budget_amount,
            budget_on_hold=budget_on_hold,
            status=status,
            receiver="$alice@uma.com",
            receiver_type=ReceivingAddressType.LUD16,
        )
        db.session.add(payment)
        await db.session.commit()

        payment = await db.session.get_one(OutgoingPayment, payment.id)
        assert payment.nip47_request_id == nip47_request.id
        assert payment.spending_cycle_id == spending_cycle.id
        assert payment.sending_currency_amount == sending_currency_amount
        assert payment.sending_currency_code == sending_currency
        assert payment.estimated_budget_currency_amount == estimated_budget_amount
        assert payment.budget_on_hold == budget_on_hold
        assert payment.status == status
        assert not payment.settled_budget_currency_amount
        assert payment.spending_cycle.id == spending_cycle.id
