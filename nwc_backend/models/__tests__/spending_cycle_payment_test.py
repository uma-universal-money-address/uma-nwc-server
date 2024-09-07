# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import (
    create_nip47_request,
    create_spending_cycle,
)
from nwc_backend.models.spending_cycle_payment import (
    PaymentStatus,
    SpendingCyclePayment,
)


async def test_spending_cycle_payment(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        nip47_request = await create_nip47_request()
        spending_cycle = await create_spending_cycle()
        estimated_amount = 100
        budget_on_hold = 110
        status = PaymentStatus.PENDING
        payment = SpendingCyclePayment(
            id=uuid4(),
            nip47_request_id=nip47_request.id,
            spending_cycle_id=spending_cycle.id,
            estimated_amount=estimated_amount,
            budget_on_hold=budget_on_hold,
            status=status,
        )
        db.session.add(payment)
        await db.session.commit()

        payment = await db.session.get_one(SpendingCyclePayment, payment.id)
        assert payment.nip47_request_id == nip47_request.id
        assert payment.spending_cycle_id == spending_cycle.id
        assert payment.estimated_amount == estimated_amount
        assert payment.budget_on_hold == budget_on_hold
        assert payment.status == status
        assert not payment.settled_amount
