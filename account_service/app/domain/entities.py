from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class Currency(str, Enum):
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"
