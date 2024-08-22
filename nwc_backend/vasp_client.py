# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import aiohttp
from quart import current_app
from uma_auth.models.execute_quote_response import ExecuteQuoteResponse
from uma_auth.models.get_balance_response import GetBalanceResponse
from uma_auth.models.get_info_response import GetInfoResponse
from uma_auth.models.list_transactions_response import ListTransactionsResponse
from uma_auth.models.lookup_user_response import LookupUserResponse
from uma_auth.models.make_invoice_request import MakeInvoiceRequest
from uma_auth.models.pay_invoice_request import PayInvoiceRequest
from uma_auth.models.pay_invoice_response import PayInvoiceResponse
from uma_auth.models.pay_to_address_request import PayToAddressRequest
from uma_auth.models.pay_to_address_response import PayToAddressResponse
from uma_auth.models.quote import Quote
from uma_auth.models.transaction import Transaction, TransactionType

from nwc_backend.exceptions import InvalidInputException, NotImplementedException


class AddressType(Enum):
    LUD16 = "lud16"
    BOLT12 = "bolt12"


@dataclass
class ReceivingAddress:
    address: str
    type: AddressType

    @staticmethod
    def from_dict(receiving_address: dict[str, str]) -> "ReceivingAddress":
        if len(receiving_address) != 1:
            raise InvalidInputException(
                "Expect `receiver` to contain exactly one address.",
            )

        address_type, address = next(iter(receiving_address.items()))
        try:
            address_type = AddressType(address_type)
        except ValueError as ex:
            raise InvalidInputException(
                "Expect `receiver` to contain address type `bolt12` or `lud16`.",
            ) from ex

        if address_type == AddressType.BOLT12:
            raise NotImplementedException("Bolt12 is not yet supported.")

        return ReceivingAddress(address=address, type=AddressType(address_type))


class LockedCurrencySide(Enum):
    SENDING = "sending"
    RECEIVING = "receiving"


class VaspUmaClient:
    def __init__(self) -> None:
        self.base_url: str = current_app.config["VASP_UMA_API_BASE_URL"]

    @staticmethod
    def instance() -> "VaspUmaClient":
        global _vasp_uma_client  # noqa: PLW0603
        if _vasp_uma_client is None:
            _vasp_uma_client = VaspUmaClient()

        return _vasp_uma_client

    async def _make_http_get(
        self, path: str, access_token: str, params: Optional[dict[str, Any]] = None
    ) -> str:
        async with aiohttp.ClientSession(base_url=self.base_url) as session:
            async with session.get(  # pyre-ignore[16]
                url=path,
                params=params,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "NWC",
                },
            ) as response:
                response.raise_for_status()
                return await response.text()

    async def _make_http_post(
        self, path: str, access_token: str, data: Optional[str] = None
    ) -> str:
        async with aiohttp.ClientSession(base_url=self.base_url) as session:
            async with session.post(  # pyre-ignore[16]
                url=path,
                data=data,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "NWC",
                },
            ) as response:
                response.raise_for_status()
                return await response.text()

    async def execute_quote(
        self, access_token: str, payment_hash: str
    ) -> ExecuteQuoteResponse:
        result = await self._make_http_post(
            path=f"/quote/{payment_hash}",
            access_token=access_token,
        )
        return ExecuteQuoteResponse.from_json(result)

    async def fetch_quote(
        self,
        access_token: str,
        sending_currency_code: str,
        receiving_currency_code: str,
        locked_currency_amount: int,
        locked_currency_side: LockedCurrencySide,
        receiver_address: ReceivingAddress,
    ) -> Quote:
        params = {
            "sending_currency_code": sending_currency_code,
            "receiving_currency_code": receiving_currency_code,
            "locked_currency_amount": locked_currency_amount,
            "locked_currency_side": locked_currency_side.value,
            "receiver_address": receiver_address.address,
        }
        result = await self._make_http_get(
            path=f"/quote/{receiver_address.type.value}",
            access_token=access_token,
            params=params,
        )
        return Quote.from_json(result)

    async def get_balance(
        self, access_token: str, currency_code: Optional[str]
    ) -> GetBalanceResponse:
        params = {"currency_code": currency_code} if currency_code else None
        result = await self._make_http_get(
            path="/balance",
            access_token=access_token,
            params=params,
        )
        return GetBalanceResponse.from_json(result)

    async def get_info(self, access_token: str) -> GetInfoResponse:
        result = await self._make_http_get(
            path="/info",
            access_token=access_token,
        )
        return GetInfoResponse.from_json(result)

    async def list_transactions(
        self,
        access_token: str,
        from_timestamp: Optional[int] = None,
        until_timestamp: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        unpaid: Optional[bool] = None,
        type: Optional[TransactionType] = None,
    ) -> ListTransactionsResponse:
        params = {}
        if from_timestamp is not None:
            params["from"] = from_timestamp
        if until_timestamp is not None:
            params["until"] = until_timestamp
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if unpaid is not None:
            params["unpaid"] = unpaid
        if type is not None:
            params["type"] = type

        result = await self._make_http_get(
            path="/transactions",
            access_token=access_token,
            params=params if params else None,
        )
        return ListTransactionsResponse.from_json(result)

    async def lookup_invoice(
        self,
        access_token: str,
        payment_hash: str,
    ) -> Transaction:
        result = await self._make_http_get(
            path=f"/invoices/{payment_hash}",
            access_token=access_token,
        )
        return Transaction.from_json(result)

    async def lookup_user(
        self,
        access_token: str,
        receiver_address: ReceivingAddress,
        base_sending_currency_code: Optional[str],
    ) -> LookupUserResponse:
        params = (
            {"base_sending_currency_code": base_sending_currency_code}
            if base_sending_currency_code
            else None
        )
        result = await self._make_http_get(
            path=f"/receiver/{receiver_address.type.value}/{receiver_address.address}",
            access_token=access_token,
            params=params,
        )
        return LookupUserResponse.from_json(result)

    async def make_invoice(
        self, access_token: str, request: MakeInvoiceRequest
    ) -> Transaction:
        result = await self._make_http_post(
            path="/invoice", access_token=access_token, data=request.to_json()
        )
        return Transaction.from_json(result)

    async def pay_invoice(
        self, access_token: str, request: PayInvoiceRequest
    ) -> PayInvoiceResponse:
        result = await self._make_http_post(
            path="/payments/bolt11", access_token=access_token, data=request.to_json()
        )
        return PayInvoiceResponse.from_json(result)

    async def pay_to_address(
        self, access_token: str, request: PayToAddressRequest, address_type: AddressType
    ) -> PayToAddressResponse:
        result = await self._make_http_post(
            path=f"/payments/{address_type.value}",
            access_token=access_token,
            data=request.to_json(),
        )
        return PayToAddressResponse.from_json(result)


_vasp_uma_client: Optional[VaspUmaClient] = None
