# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from nwc_backend.models.nip47_budget import Nip47BudgetCurrency, Nip47BudgetResponse
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def get_budget(access_token: str, request: Nip47Request) -> Nip47BudgetResponse:
    current_spending_limit = request.get_spending_limit()
    if not current_spending_limit:
        return Nip47BudgetResponse()

    spending_cycle = await current_spending_limit.get_current_spending_cycle()
    budget_currency = spending_cycle.limit_currency
    if budget_currency == "SAT":
        return Nip47BudgetResponse(
            total_budget_msats=spending_cycle.limit_amount * 1000,
            remaining_budget_msats=spending_cycle.get_available_budget_amount() * 1000,
            renews_at=(
                round(spending_cycle.end_time.timestamp())
                if spending_cycle.end_time
                else None
            ),
        )

    budget_estimate_response = await VaspUmaClient.instance().get_budget_estimate(
        access_token=access_token,
        sending_currency_code=spending_cycle.limit_currency,
        sending_currency_amount=spending_cycle.limit_amount,
        budget_currency_code="SAT",
    )

    total_budget_sats = budget_estimate_response.estimated_budget_currency_amount
    remaining_budget_sats = round(
        total_budget_sats
        / spending_cycle.limit_amount
        * spending_cycle.get_available_budget_amount()
    )

    return Nip47BudgetResponse(
        currency=Nip47BudgetCurrency(
            code=budget_currency,
            total_budget=spending_cycle.limit_amount,
            remaining_budget=spending_cycle.get_available_budget_amount(),
            # TODO(Jeremy): Get these from the VASP somehow.
            symbol="",
            name="",
            decimals=2,
        ),
        total_budget_msats=total_budget_sats * 1000,
        remaining_budget_msats=remaining_budget_sats * 1000,
        renews_at=(
            round(spending_cycle.end_time.timestamp())
            if spending_cycle.end_time
            else None
        ),
    )
