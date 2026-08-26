from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import IntEnum


class Confidence(IntEnum):
    NO_MATCH = 0
    POSSIBLE = 1
    MATCH = 2


class ProbeRisk(IntEnum):
    """Relative chance that a probe write is meaningful to the wrong device."""

    PASSIVE = 0
    REGISTER = 1
    COMMAND = 2


@dataclass(frozen=True)
class ProbeResult:
    confidence: Confidence
    evidence: Mapping[str, str] = field(default_factory=dict)
    name: str | None = None
    score: int | None = None
    max_score: int | None = None

    def __post_init__(self) -> None:
        if (self.score is None) != (self.max_score is None):
            raise ValueError("score and max_score must be provided together")
        if self.score is not None and (
            self.max_score is None or self.max_score < 1 or not 0 <= self.score <= self.max_score
        ):
            raise ValueError("score must be between zero and max_score")

    @classmethod
    def no_match(
        cls,
        evidence: Mapping[str, str] | None = None,
        *,
        score: int | None = None,
        max_score: int | None = None,
    ) -> ProbeResult:
        return cls(Confidence.NO_MATCH, evidence or {}, score=score, max_score=max_score)

    @classmethod
    def possible(
        cls,
        evidence: Mapping[str, str] | None = None,
        *,
        name: str | None = None,
        score: int | None = None,
        max_score: int | None = None,
    ) -> ProbeResult:
        return cls(Confidence.POSSIBLE, evidence or {}, name, score, max_score)

    @classmethod
    def match(
        cls,
        evidence: Mapping[str, str] | None = None,
        *,
        name: str | None = None,
        score: int | None = None,
        max_score: int | None = None,
    ) -> ProbeResult:
        return cls(Confidence.MATCH, evidence or {}, name, score, max_score)

    def with_score_bonus(self, *, earned: int, available: int) -> ProbeResult:
        """Return a result with weak contextual evidence added to its score."""

        if self.score is None or self.max_score is None:
            return self
        if available < 0 or not 0 <= earned <= available:
            raise ValueError("score bonus must be between zero and available")
        return ProbeResult(
            self.confidence,
            self.evidence,
            self.name,
            self.score + earned,
            self.max_score + available,
        )
