# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os

DATABASE_URI: str = "sqlite+pysqlite:///" + os.path.join(
    os.getcwd(), "instance", "nwc.sqlite"
)

FRONTEND_BUILD_PATH = "../nwc-frontend/dist"
NWC_FRONTEND_NEW_APP_PAGE = "http://localhost:3000/apps/new"
UMA_VASP_LOGIN_URL = "http://127.0.0.1:5001/apps/new"
