# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os

import aiohttp
from uma_auth.models.invoice import Invoice
from uma_auth.models.make_invoice_request import MakeInvoiceRequest
from uma_auth.models.pay_invoice_request import PayInvoiceRequest
from uma_auth.models.pay_invoice_response import PayInvoiceResponse
from uma_auth.models.pay_to_address_request import PayToAddressRequest
from uma_auth.models.pay_to_address_response import PayToAddressResponse


class VaspUmaClient:
    def __init__(self) -> None:
        self.base_url: str = os.environ["VASP_UMA_API_BASE_URL"]

    async def _make_http_post(self, path: str, access_token: str, data: str) -> str:
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

    async def make_invoice(
        self, access_token: str, request: MakeInvoiceRequest
    ) -> Invoice:
        result = await self._make_http_post(
            path="/invoice", access_token=access_token, data=request.to_json()
        )
        return Invoice.from_json(result)

    async def pay_invoice(
        self, access_token: str, request: PayInvoiceRequest
    ) -> PayInvoiceResponse:
        result = await self._make_http_post(
            path="/payments/bolt11", access_token=access_token, data=request.to_json()
        )
        return PayInvoiceResponse.from_json(result)

    async def pay_to_address(
        self, access_token: str, request: PayToAddressRequest
    ) -> PayToAddressResponse:
        result = await self._make_http_post(
            path="/payments/lnurl", access_token=access_token, data=request.to_json()
        )
        return PayToAddressResponse.from_json(result)


vasp_uma_client = VaspUmaClient()
