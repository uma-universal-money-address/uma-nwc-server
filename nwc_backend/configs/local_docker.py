# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os

DATABASE_URI: str = "sqlite+pysqlite:///" + os.path.join(
    os.getcwd(), "instance", "nwc.sqlite"
)

VASP_NWC_SERVER_SHARED_SECRET = "secret"
FRONTEND_BUILD_PATH = "../static"
NWC_FRONTEND_NEW_APP_PAGE = "http://localhost:3000/apps/new"
UMA_VASP_LOGIN_URL = "http://127.0.0.1:5001/apps/new"

VASP_SUPPORTED_COMMANDS = [
    "pay_invoice",
    "make_invoice",
    "lookup_invoice",
    "get_balance",
    "get_info",
    "list_transactions",
    "pay_keysend",
    "lookup_user",
    "fetch_quote",
    "execute_quote",
    "pay_to_address",
]