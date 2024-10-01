# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from nwc_backend.models.nip47_budget import Nip47BudgetCurrency, Nip47BudgetResponse
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def get_budget(access_token: str, request: Nip47Request) -> Nip47BudgetResponse:
    current_spending_limit = request.get_spending_limit()
    if not current_spending_limit:
        return Nip47BudgetResponse()

    current_cycle_remaining_amount = (
        await current_spending_limit.get_current_cycle_total_remaining()
    )
    budget_currency = request.nwc_connection.budget_currency
    current_cycle_end_time = current_spending_limit.get_current_cycle_end_time()
    current_cycle_renews_at = (
        round(current_cycle_end_time.timestamp()) if current_cycle_end_time else None
    )
    if budget_currency.code == "SAT":
        used_budget_sats = (
            current_spending_limit.amount - current_cycle_remaining_amount
        )
        return Nip47BudgetResponse(
            total_budget=current_spending_limit.amount * 1000,
            used_budget=used_budget_sats * 1000,
            renews_at=current_cycle_renews_at,
            renewal_period=current_spending_limit.frequency.value,
        )

    budget_estimate_response = await VaspUmaClient.instance().get_budget_estimate(
        access_token=access_token,
        sending_currency_code=budget_currency.code,
        sending_currency_amount=current_spending_limit.amount,
        budget_currency_code="SAT",
    )

    total_budget_sats = budget_estimate_response.estimated_budget_currency_amount
    remaining_budget_sats = round(
        total_budget_sats
        / current_spending_limit.amount
        * current_cycle_remaining_amount
    )
    used_budget_sats = total_budget_sats - remaining_budget_sats

    return Nip47BudgetResponse(
        currency=Nip47BudgetCurrency(
            code=budget_currency.code,
            total_budget=current_spending_limit.amount,
            used_budget=current_spending_limit.amount - current_cycle_remaining_amount,
            symbol=budget_currency.symbol,
            name=budget_currency.name,
            decimals=budget_currency.decimals,
        ),
        total_budget=total_budget_sats * 1000,
        used_budget=used_budget_sats * 1000,
        renews_at=current_cycle_renews_at,
        renewal_period=current_spending_limit.frequency.value,
    )
