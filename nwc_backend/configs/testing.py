# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict


DATABASE_URI: str = "sqlite+aiosqlite:///:memory:"
SECRET_KEY = "tests_secret_key"
UMA_VASP_JWT_PUBKEY = "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEEVs/o5+uQbTjL3chynL4wXgUg2R9\nq9UU8I5mEovUf86QZ7kOBIjJwqnzD1omageEHWwHdBO6B+dFabmdT9POxg==\n-----END PUBLIC KEY-----"
FRONTEND_BUILD_PATH = "../nwc-frontend/dist"
UMA_VASP_LOGIN_URL = "http://local:5001/auth/nwcsession"
VASP_NAME = "Pink Drink NWC"
NOSTR_PRIVKEY = "nsec166ah7ez498kjl87a088yn34gvcjpzmy9eymuwwgtwcywh84j865s0qxnul"
RELAY = "wss://fake.relay.url"
UMA_VASP_TOKEN_EXCHANGE_URL = "http://local:5001/umanwc/token"
VASP_UMA_API_BASE_URL = "https://fake.vasp.uma.api.url"
NWC_APP_ROOT_URL = "http://localhost:8080"
QUART_ENV = "testing"
BUDGET_BUFFER_MULTIPLIER = 1.1

VASP_SUPPORTED_COMMANDS = [
    "pay_invoice",
    "make_invoice",
    "lookup_invoice",
    "get_balance",
    "get_budget",
    "get_info",
    "list_transactions",
    "pay_keysend",
    "lookup_user",
    "fetch_quote",
    "execute_quote",
    "pay_to_address",
]
