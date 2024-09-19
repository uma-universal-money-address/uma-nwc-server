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
    budget_currency = current_spending_limit.currency.code
    current_cycle_end_time = current_spending_limit.get_current_cycle_end_time()
    current_cycle_renews_at = (
        round(current_cycle_end_time.timestamp()) if current_cycle_end_time else None
    )
    if budget_currency == "SAT":
        return Nip47BudgetResponse(
            total_budget_msats=current_spending_limit.amount * 1000,
            remaining_budget_msats=current_cycle_remaining_amount * 1000,
            renews_at=current_cycle_renews_at,
        )

    budget_estimate_response = await VaspUmaClient.instance().get_budget_estimate(
        access_token=access_token,
        sending_currency_code=budget_currency,
        sending_currency_amount=current_spending_limit.amount,
        budget_currency_code="SAT",
    )

    total_budget_sats = budget_estimate_response.estimated_budget_currency_amount
    remaining_budget_sats = round(
        total_budget_sats
        / current_spending_limit.amount
        * current_cycle_remaining_amount
    )

    return Nip47BudgetResponse(
        currency=Nip47BudgetCurrency(
            code=budget_currency,
            total_budget=current_spending_limit.amount,
            remaining_budget=current_cycle_remaining_amount,
            # TODO(Jeremy): Get these from the VASP somehow.
            symbol="",
            name="",
            decimals=2,
        ),
        total_budget_msats=total_budget_sats * 1000,
        remaining_budget_msats=remaining_budget_sats * 1000,
        renews_at=current_cycle_renews_at,
    )
