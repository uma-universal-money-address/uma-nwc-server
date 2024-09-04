from enum import Enum
from nwc_backend.models.nip47_request_method import Nip47RequestMethod


class PermissionsGroup(Enum):
    SEND_PAYMENTS = "send_payments"
    READ_BALANCE = "read_balance"
    READ_TRANSACTIONS = "read_transactions"
    RECEIVE_PAYMENTS = "receive_payments"
    ALWAYS_GRANTED = "always_granted"


METHOD_TO_PERMISSIONS_GROUP = {
    Nip47RequestMethod.MAKE_INVOICE.value: PermissionsGroup.RECEIVE_PAYMENTS,
    Nip47RequestMethod.GET_BALANCE.value: PermissionsGroup.READ_BALANCE,
    Nip47RequestMethod.PAY_KEYSEND.value: PermissionsGroup.SEND_PAYMENTS,
    Nip47RequestMethod.PAY_INVOICE.value: PermissionsGroup.SEND_PAYMENTS,
    Nip47RequestMethod.FETCH_QUOTE.value: PermissionsGroup.SEND_PAYMENTS,
    Nip47RequestMethod.EXECUTE_QUOTE.value: PermissionsGroup.SEND_PAYMENTS,
    Nip47RequestMethod.PAY_TO_ADDRESS.value: PermissionsGroup.SEND_PAYMENTS,
    Nip47RequestMethod.LOOKUP_INVOICE.value: PermissionsGroup.READ_TRANSACTIONS,
    Nip47RequestMethod.LIST_TRANSACTIONS.value: PermissionsGroup.READ_TRANSACTIONS,
    Nip47RequestMethod.LOOKUP_USER.value: PermissionsGroup.ALWAYS_GRANTED,
    Nip47RequestMethod.GET_INFO.value: PermissionsGroup.ALWAYS_GRANTED,
    # groups map to themselves
    PermissionsGroup.SEND_PAYMENTS.value: PermissionsGroup.SEND_PAYMENTS,
    PermissionsGroup.RECEIVE_PAYMENTS.value: PermissionsGroup.RECEIVE_PAYMENTS,
    PermissionsGroup.READ_BALANCE.value: PermissionsGroup.READ_BALANCE,
    PermissionsGroup.READ_TRANSACTIONS.value: PermissionsGroup.READ_TRANSACTIONS,
}

PERMISSIONS_GROUP_TO_METHODS = {
    PermissionsGroup.RECEIVE_PAYMENTS: [
        Nip47RequestMethod.MAKE_INVOICE.value,
    ],
    PermissionsGroup.SEND_PAYMENTS: [
        Nip47RequestMethod.PAY_INVOICE.value,
        Nip47RequestMethod.PAY_KEYSEND.value,
        Nip47RequestMethod.EXECUTE_QUOTE.value,
        Nip47RequestMethod.PAY_TO_ADDRESS.value,
        Nip47RequestMethod.FETCH_QUOTE.value,
    ],
    PermissionsGroup.READ_BALANCE: [
        Nip47RequestMethod.GET_BALANCE.value,
    ],
    PermissionsGroup.READ_TRANSACTIONS: [
        Nip47RequestMethod.LIST_TRANSACTIONS.value,
        Nip47RequestMethod.LOOKUP_INVOICE.value,
    ],
    PermissionsGroup.ALWAYS_GRANTED: [
        Nip47RequestMethod.LOOKUP_USER.value,
        Nip47RequestMethod.GET_INFO.value,
    ],
}
