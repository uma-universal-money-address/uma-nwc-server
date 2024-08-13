import os

os.environ["NOSTR_PRIVKEY"] = (
    "nsec166ah7ez498kjl87a088yn34gvcjpzmy9eymuwwgtwcywh84j865s0qxnul"
)
os.environ["RELAY"] = "wss://fake.relay.url"
os.environ["VASP_UMA_API_BASE_URL"] = "https://fake.vasp.uma.api.url"

import pytest
from nwc_backend.models.nip47_request import Nip47Request, ErrorCode, Nip47Error
from nwc_backend.vasp_client import ReceivingAddress, VaspUmaClient, LookupUserResponse
from nwc_backend.event_handlers.lookup_user_handler import lookup_user
from uma_auth.models.currency_preference import CurrencyPreference


class MockVaspUmaClient(VaspUmaClient):
    lookup_user_response = LookupUserResponse(
        currencies=[
            CurrencyPreference(
                code="USD",
                symbol="$",
                name="US Dollar",
                multiplier=1000,
                decimals=2,
                min=1000,
                max=1000000,
            )
        ]
    )

    async def lookup_user(
        self,
        access_token: str,
        receiving_address: ReceivingAddress,
        base_sending_currency_code: str,
    ) -> LookupUserResponse:
        return self.lookup_user_response


@pytest.fixture
def vasp_client_mock():
    return MockVaspUmaClient()


async def test_lookup_user_success(vasp_client_mock):
    access_token = "your_access_token"
    request = Nip47Request(
        params={
            "receiver": {"lud16": "$alice@vasp.net"},
            "base_sending_currency_code": "USD",
        }
    )

    result = await lookup_user(access_token, request, vasp_client_mock)

    assert isinstance(result, dict)
    assert result == vasp_client_mock.lookup_user_response.to_dict()


async def test_lookup_user_missing_receiver(vasp_client_mock):
    access_token = "your_access_token"
    request = Nip47Request(params={})

    result = await lookup_user(access_token, request, vasp_client_mock)

    assert isinstance(result, Nip47Error)
    assert result.code == ErrorCode.OTHER
    assert result.message == "Require receiver in the request params."


async def test_lookup_user_multiple_receivers(vasp_client_mock):
    access_token = "your_access_token"
    request = Nip47Request(
        params={"receiver": {"bolt12": "bolt12_address", "lud16": "lud16_address"}}
    )

    result = await lookup_user(access_token, request, vasp_client_mock)

    assert isinstance(result, Nip47Error)
    assert result.code == ErrorCode.OTHER
    assert result.message == "Expect receiver to contain exactly one address."
