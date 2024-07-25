# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os

DATABASE_URI: str = "sqlite+pysqlite:///" + os.path.join(
    os.getcwd(), "instance", "nwc.sqlite"
)

FRONTEND_BUILD_PATH = "../nwc-frontend/dist"
