from typing import Optional


class Nip47BudgetCurrency:
    def __init__(
        self,
        code: str,
        symbol: str,
        name: str,
        decimals: int,
        remaining_budget: int,
        total_budget: int,
    ):
        self.code = code
        self.symbol = symbol
        self.name = name
        self.decimals = decimals
        self.remaining_budget = remaining_budget
        self.total_budget = total_budget

    def to_dict(self):
        return {
            "code": self.code,
            "symbol": self.symbol,
            "name": self.name,
            "decimals": self.decimals,
            "remaining_budget": self.remaining_budget,
            "total_budget": self.total_budget,
        }


class Nip47BudgetResponse:
    def __init__(
        self,
        remaining_budget_msats: Optional[int] = None,
        total_budget_msats: Optional[int] = None,
        renews_at: Optional[int] = None,
        currency: Optional[Nip47BudgetCurrency] = None,
    ):
        self.remaining_budget_msats = remaining_budget_msats
        self.total_budget_msats = total_budget_msats
        self.renews_at = renews_at
        self.currency = currency

    def to_dict(self):
        if self.remaining_budget_msats is None:
            return {}
        result = {
            "remaining_budget_msats": self.remaining_budget_msats,
            "total_budget_msats": self.total_budget_msats,
        }

        if self.renews_at is not None:
            result["renews_at"] = self.renews_at

        if self.currency is not None:
            result["currency"] = self.currency.to_dict()

        return result
