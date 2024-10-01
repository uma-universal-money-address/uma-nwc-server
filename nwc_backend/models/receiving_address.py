# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from nwc_backend.exceptions import InvalidInputException, NotImplementedException


class ReceivingAddressType(Enum):
    LUD16 = "lud16"
    BOLT12 = "bolt12"
    BOLT11 = "bolt11"
    NODE_PUBKEY = "node_pubkey"


@dataclass
class ReceivingAddress:
    address: str
    type: ReceivingAddressType

    @staticmethod
    def from_dict(
        receiving_address: dict[str, str],
        expected_address_type: Optional[ReceivingAddressType] = None,
    ) -> "ReceivingAddress":
        if len(receiving_address) != 1:
            raise InvalidInputException(
                "Expect `receiver` to contain exactly one address.",
            )

        address_type, address = next(iter(receiving_address.items()))
        try:
            address_type = ReceivingAddressType(address_type)
        except ValueError as ex:
            raise InvalidInputException(
                "Unexpected `receiver` address type.",
            ) from ex

        if address_type == ReceivingAddressType.BOLT12:
            raise NotImplementedException("Bolt12 is not yet supported.")

        if expected_address_type and address_type != expected_address_type:
            raise InvalidInputException(
                f"Expected `receiver` to have address type {expected_address_type.value}, {address_type.value} found."
            )

        return ReceivingAddress(
            address=address, type=ReceivingAddressType(address_type)
        )
