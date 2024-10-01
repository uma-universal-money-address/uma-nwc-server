# pyre-strict

from typing import Any, Optional
from urllib.parse import urlparse

import aiohttp
from quart import current_app
from uma_auth.models.budget_estimate_response import BudgetEstimateResponse
from uma_auth.models.execute_quote_request import ExecuteQuoteRequest
from uma_auth.models.execute_quote_response import ExecuteQuoteResponse
from uma_auth.models.get_balance_response import GetBalanceResponse
from uma_auth.models.get_info_response import GetInfoResponse
from uma_auth.models.list_transactions_response import ListTransactionsResponse
from uma_auth.models.locked_currency_side import LockedCurrencySide
from uma_auth.models.lookup_user_response import LookupUserResponse
from uma_auth.models.make_invoice_request import MakeInvoiceRequest
from uma_auth.models.pay_invoice_request import PayInvoiceRequest
from uma_auth.models.pay_invoice_response import PayInvoiceResponse
from uma_auth.models.pay_keysend_request import PayKeysendRequest
from uma_auth.models.pay_keysend_response import PayKeysendResponse
from uma_auth.models.pay_to_address_request import PayToAddressRequest
from uma_auth.models.pay_to_address_response import PayToAddressResponse
from uma_auth.models.quote import Quote
from uma_auth.models.transaction import Transaction, TransactionType

from nwc_backend.exceptions import VaspErrorResponseException
from nwc_backend.models.receiving_address import ReceivingAddress, ReceivingAddressType


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
        base_url_parts = urlparse(self.base_url)
        base_url_without_path = f"{base_url_parts.scheme}://{base_url_parts.netloc}"
        base_url_path = base_url_parts.path
        async with aiohttp.ClientSession(base_url=base_url_without_path) as session:
            async with session.get(  # pyre-ignore[16]
                url=f"{base_url_path}{path}",
                params=params,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "NWC",
                },
            ) as response:
                text = await response.text()
                if not response.ok:
                    raise VaspErrorResponseException(
                        http_status=response.status, response=text
                    )
                return text

    async def _make_http_post(
        self, path: str, access_token: str, data: Optional[str] = None
    ) -> str:
        base_url_parts = urlparse(self.base_url)
        base_url_without_path = f"{base_url_parts.scheme}://{base_url_parts.netloc}"
        base_url_path = base_url_parts.path
        async with aiohttp.ClientSession(base_url=base_url_without_path) as session:
            async with session.post(  # pyre-ignore[16]
                url=f"{base_url_path}{path}",
                data=data,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "NWC",
                },
            ) as response:
                text = await response.text()
                if not response.ok:
                    raise VaspErrorResponseException(
                        http_status=response.status, response=text
                    )
                return text

    async def execute_quote(
        self,
        access_token: str,
        payment_hash: str,
        request: ExecuteQuoteRequest,
    ) -> ExecuteQuoteResponse:
        result = await self._make_http_post(
            path=f"/quote/{payment_hash}",
            access_token=access_token,
            data=request.to_json(),
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

    async def pay_keysend(
        self, access_token: str, request: PayKeysendRequest
    ) -> PayKeysendResponse:
        result = await self._make_http_post(
            path="/payments/keysend", access_token=access_token, data=request.to_json()
        )
        return PayKeysendResponse.from_json(result)

    async def pay_to_address(
        self,
        access_token: str,
        request: PayToAddressRequest,
        address_type: ReceivingAddressType,
    ) -> PayToAddressResponse:
        result = await self._make_http_post(
            path=f"/payments/{address_type.value}",
            access_token=access_token,
            data=request.to_json(),
        )
        return PayToAddressResponse.from_json(result)

    async def get_budget_estimate(
        self,
        access_token: str,
        sending_currency_code: str,
        sending_currency_amount: int,
        budget_currency_code: str,
    ) -> BudgetEstimateResponse:
        params = {
            "sending_currency_code": sending_currency_code,
            "sending_currency_amount": sending_currency_amount,
            "budget_currency_code": budget_currency_code,
        }
        result = await self._make_http_get(
            path="/budget_estimate",
            access_token=access_token,
            params=params,
        )
        return BudgetEstimateResponse.from_json(result)


_vasp_uma_client: Optional[VaspUmaClient] = None
