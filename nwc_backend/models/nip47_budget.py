from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Nip47BudgetCurrency:
    code: str
    symbol: str
    name: str
    decimals: int
    used_budget: int
    total_budget: int


@dataclass
class Nip47BudgetResponse:
    used_budget: Optional[int] = None
    total_budget: Optional[int] = None
    renews_at: Optional[int] = None
    renewal_period: Optional[str] = None
    currency: Optional[Nip47BudgetCurrency] = None

    def to_dict(self):
        if self.used_budget is None:
            return {}
        return {k: v for k, v in asdict(self).items() if v is not None}
