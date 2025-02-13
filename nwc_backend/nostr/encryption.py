from typing import List


NWC_ENCRYPTION_SCHEMES_SUPPORTED: List[str] = ["nip44_v2", "nip04"]


def is_encryption_supported(scheme: str) -> bool:
    return scheme in NWC_ENCRYPTION_SCHEMES_SUPPORTED
