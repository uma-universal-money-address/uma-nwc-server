from dataclasses import dataclass
from functools import total_ordering
from typing import List


NWC_VERSIONS_SUPPORTED: List[str] = ["0.0", "1.0"]


@total_ordering
@dataclass
class ParsedVersion:
    major: int
    minor: int

    @classmethod
    def load(cls, version: str) -> "ParsedVersion":
        [major, minor] = version.split(".")
        return ParsedVersion(major=int(major), minor=int(minor))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    def __lt__(self, other: "ParsedVersion") -> bool:
        return self.major < other.major or (
            self.major == other.major and self.minor < other.minor
        )


def is_version_supported(version: ParsedVersion) -> bool:
    for version_str in NWC_VERSIONS_SUPPORTED:
        supported_version = ParsedVersion.load(version_str)
        if version.major == supported_version.major:
            return version.minor <= supported_version.minor
    return False
