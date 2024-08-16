# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Any


def exclude_none_values(dictionary: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in dictionary.items() if value is not None}
