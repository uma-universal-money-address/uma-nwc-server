# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from enum import Enum


class Nip47RequestMethod(Enum):
    PAY_INVOICE = "pay_invoice"
    MAKE_INVOICE = "make_invoice"
    LOOKUP_INVOICE = "lookup_invoice"
    GET_BALANCE = "get_balance"
    GET_BUDGET = "get_budget"
    GET_INFO = "get_info"
    LIST_TRANSACTIONS = "list_transactions"
    PAY_KEYSEND = "pay_keysend"
    LOOKUP_USER = "lookup_user"
    FETCH_QUOTE = "fetch_quote"
    EXECUTE_QUOTE = "execute_quote"
    PAY_TO_ADDRESS = "pay_to_address"

    @staticmethod
    def get_values() -> list[str]:
        return [method.value for method in Nip47RequestMethod]
