from datetime import timedelta
from enum import Enum
from typing import Optional


class SpendingLimitFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    # none frequency means the limit is for all time
    # so the connection can only ever be used for the limit amount
    NONE = "none"

    @staticmethod
    def get_time_delta(frequency: "SpendingLimitFrequency") -> Optional[timedelta]:
        match frequency:
            case SpendingLimitFrequency.DAILY:
                return timedelta(days=1)
            case SpendingLimitFrequency.WEEKLY:
                return timedelta(days=7)
            case SpendingLimitFrequency.MONTHLY:
                return timedelta(days=30)
            case SpendingLimitFrequency.YEARLY:
                return timedelta(days=365)
            case SpendingLimitFrequency.NONE:
                return None
