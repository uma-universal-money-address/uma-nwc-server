import asyncio
import json
from urllib.parse import urlencode, urlparse, urlunparse

from quart.app import QuartClient

from nwc_backend.models.__tests__.model_examples import (
    create_nwc_connection,
    create_outgoing_payment,
    create_spending_cycle,
    create_spending_limit,
)
from nwc_backend.models.outgoing_payment import PaymentStatus


async def test_get_outgoing_payments(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        nwc_connection = await create_nwc_connection()
        payment1 = await create_outgoing_payment(  # no spending limit
            nwc_connection=nwc_connection,
            sending_currency_amount=10,
            sending_currency_code="USD",
        )
        await asyncio.sleep(1)
        spending_limit = await create_spending_limit(nwc_connection=nwc_connection)
        spending_cycle = await create_spending_cycle(spending_limit=spending_limit)
        payment2 = await create_outgoing_payment(  # has spending limit
            nwc_connection=nwc_connection,
            spending_cycle=spending_cycle,
            sending_currency_amount=5,
            sending_currency_code="USD",
            budget_on_hold=6,
        )
        await asyncio.sleep(1)
        payment3 = await create_outgoing_payment(  # has spending limit
            nwc_connection=nwc_connection,
            spending_cycle=spending_cycle,
            sending_currency_amount=7,
            sending_currency_code="USD",
            budget_on_hold=8,
            status=PaymentStatus.PENDING,
        )

    async with test_client.session_transaction() as session:
        session["user_id"] = nwc_connection.user_id

    # first fetch
    request_params = {"limit": 1}
    url_parts = list(urlparse(f"/api/connection/{nwc_connection.id}/transactions"))
    query = urlencode(request_params)
    url_parts[4] = query
    response = await test_client.get(urlunparse(url_parts))

    assert response.status_code == 200
    result = json.loads((await response.data).decode())
    assert result["count"] == 3
    [result_tx_3] = result["transactions"]
    assert result_tx_3["id"] == str(payment3.id)
    assert result_tx_3["sending_currency_code"] == payment3.sending_currency_code
    assert result_tx_3["sending_currency_amount"] == payment3.sending_currency_amount
    assert result_tx_3["status"] == payment3.status.value
    assert result_tx_3["budget_currency_amount"] is None
    assert result_tx_3["budget_on_hold"] == payment3.budget_on_hold
    assert result_tx_3["receiver"] == payment3.receiver
    assert result_tx_3["receiver_type"] == payment3.receiver_type.name

    # second fetch
    request_params = {"limit": 3, "offset": 1}
    url_parts = list(urlparse(f"/api/connection/{nwc_connection.id}/transactions"))
    query = urlencode(request_params)
    url_parts[4] = query
    response = await test_client.get(urlunparse(url_parts))

    assert response.status_code == 200
    result = json.loads((await response.data).decode())
    assert result["count"] == 2
    [result_tx_2, result_tx_1] = result["transactions"]
    assert result_tx_2["id"] == str(payment2.id)
    assert result_tx_2["sending_currency_code"] == payment2.sending_currency_code
    assert result_tx_2["sending_currency_amount"] == payment2.sending_currency_amount
    assert result_tx_2["status"] == payment2.status.value
    assert (
        result_tx_2["budget_currency_amount"] == payment2.settled_budget_currency_amount
    )
    assert result_tx_2["budget_on_hold"] is None
    assert result_tx_2["receiver"] == payment2.receiver
    assert result_tx_2["receiver_type"] == payment2.receiver_type.name
    assert result_tx_1["id"] == str(payment1.id)
    assert result_tx_1["sending_currency_code"] == payment1.sending_currency_code
    assert result_tx_1["sending_currency_amount"] == payment1.sending_currency_amount
    assert result_tx_1["status"] == payment1.status.value
    assert result_tx_1["budget_currency_amount"] is None
    assert result_tx_1["budget_on_hold"] is None
    assert result_tx_1["receiver"] == payment1.receiver
    assert result_tx_1["receiver_type"] == payment1.receiver_type.name


async def test_get_outgoing_payments__empty(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        nwc_connection = await create_nwc_connection()

    async with test_client.session_transaction() as session:
        session["user_id"] = nwc_connection.user_id

    request_params = {"limit": 10}
    url_parts = list(urlparse(f"/api/connection/{nwc_connection.id}/transactions"))
    query = urlencode(request_params)
    url_parts[4] = query
    response = await test_client.get(urlunparse(url_parts))

    assert response.status_code == 200
    result = json.loads((await response.data).decode())
    assert result["count"] == 0
    assert len(result["transactions"]) == 0
