# pyre-strict

import os
import secrets
from typing import List, Optional

DATABASE_URI: str = "sqlite+aiosqlite:///" + os.path.join(
    os.getcwd(), "instance", "nwc.sqlite"
)
SECRET_KEY: str = secrets.token_hex(32)

UMA_VASP_JWT_PUBKEY = "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEEVs/o5+uQbTjL3chynL4wXgUg2R9\nq9UU8I5mEovUf86QZ7kOBIjJwqnzD1omageEHWwHdBO6B+dFabmdT9POxg==\n-----END PUBLIC KEY-----"
UMA_VASP_JWT_AUD: Optional[str] = None
UMA_VASP_JWT_ISS: Optional[str] = None
FRONTEND_BUILD_PATH = "../static"
UMA_VASP_LOGIN_URL = "http://local:5001/auth/nwcsession"
UMA_VASP_TOKEN_EXCHANGE_URL = "http://local:5001/umanwc/token"
VASP_UMA_API_BASE_URL = "http://local:5001/umanwc"
VASP_NAME = "Pink Drink NWC"
NWC_APP_ROOT_URL = "http://localhost:8080"
# If you want to host the whole app in a subpath, set the BASE_PATH to the subpath and update
# NWC_APP_ROOT_URL to include the subpath.
# BASE_PATH = "/nwc"

# Replace with your own constant private key via `openssl rand -hex 32` if you want.
NOSTR_PRIVKEY: str = secrets.token_hex(32)
RELAY = "wss://relay.getalby.com/v1"

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

# NIP-68 client app authorities which can verify app identity events.
CLIENT_APP_AUTHORITIES: List[str] = [
    # "nprofile1qqstse98yvaykl3k2yez3732tmsc9vaq8c3uhex0s4qp4dl8fczmp9spp4mhxue69uhkummn9ekx7mq26saje" # Lightspark at nos.lol
]
