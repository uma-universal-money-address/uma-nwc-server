from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Nip47BudgetCurrency:
    code: str
    symbol: str
    name: str
    decimals: int
    remaining_budget: int
    total_budget: int


@dataclass
class Nip47BudgetResponse:
    remaining_budget_msats: Optional[int] = None
    total_budget_msats: Optional[int] = None
    renews_at: Optional[int] = None
    currency: Optional[Nip47BudgetCurrency] = None

    def to_dict(self):
        if self.remaining_budget_msats is None:
            return {}
        return {k: v for k, v in asdict(self).items() if v is not None}
