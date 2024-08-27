from enum import Enum


class SpendingLimitFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    # none frequency means the limit is for all time
    # so the connection can only ever be used for the limit amount
    NONE = "none"
