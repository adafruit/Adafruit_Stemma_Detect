from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import IntEnum


class Confidence(IntEnum):
    NO_MATCH = 0
    POSSIBLE = 1
    MATCH = 2


@dataclass(frozen=True)
class ProbeResult:
    confidence: Confidence
    evidence: Mapping[str, str] = field(default_factory=dict)
    name: str | None = None

    @classmethod
    def no_match(cls, evidence: Mapping[str, str] | None = None) -> ProbeResult:
        return cls(Confidence.NO_MATCH, evidence or {})

    @classmethod
    def possible(cls, evidence: Mapping[str, str] | None = None) -> ProbeResult:
        return cls(Confidence.POSSIBLE, evidence or {})

    @classmethod
    def match(
        cls,
        evidence: Mapping[str, str] | None = None,
        *,
        name: str | None = None,
    ) -> ProbeResult:
        return cls(Confidence.MATCH, evidence or {}, name)
