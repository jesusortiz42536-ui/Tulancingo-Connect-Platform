"""
Data models for the Denarytor civic forum.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List


class ReportCategory(str, Enum):
    INFRASTRUCTURE = "infrastructure"
    PUBLIC_SAFETY = "public_safety"
    ENVIRONMENT = "environment"
    HEALTH = "health"
    OTHER = "other"


class ReportStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class DebateStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class VoteChoice(str, Enum):
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


@dataclass
class Report:
    """
    A citizen-submitted public report (e.g. pothole, broken streetlight).
    """

    title: str
    description: str
    category: ReportCategory
    location: str
    submitted_by: str           # citizen user ID
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ReportStatus = ReportStatus.SUBMITTED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Report title must not be empty.")
        if not self.description.strip():
            raise ValueError("Report description must not be empty.")

    def start_review(self) -> None:
        """Move the report to under-review status."""
        if self.status != ReportStatus.SUBMITTED:
            raise RuntimeError(f"Report {self.report_id} is not in SUBMITTED status.")
        self.status = ReportStatus.UNDER_REVIEW
        self.updated_at = datetime.now(timezone.utc)

    def resolve(self) -> None:
        """Mark the report as resolved."""
        if self.status not in (ReportStatus.SUBMITTED, ReportStatus.UNDER_REVIEW):
            raise RuntimeError(f"Cannot resolve report {self.report_id} from status {self.status}.")
        self.status = ReportStatus.RESOLVED
        self.updated_at = datetime.now(timezone.utc)

    def reject(self, reason: str = "") -> None:
        """Reject the report (e.g. duplicate or out of scope)."""
        if self.status == ReportStatus.RESOLVED:
            raise RuntimeError(f"Cannot reject an already-resolved report {self.report_id}.")
        self.status = ReportStatus.REJECTED
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class Vote:
    """A citizen vote on a community debate proposal."""

    debate_id: str
    citizen_id: str
    choice: VoteChoice
    vote_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cast_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Debate:
    """
    A community debate topic where citizens can vote and comment.
    """

    title: str
    description: str
    created_by: str         # moderator / authority user ID
    debate_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: DebateStatus = DebateStatus.OPEN
    votes: List[Vote] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Debate title must not be empty.")

    def cast_vote(self, citizen_id: str, choice: VoteChoice) -> Vote:
        """Register a citizen vote on this debate."""
        if self.status != DebateStatus.OPEN:
            raise RuntimeError(f"Debate {self.debate_id} is closed; votes are no longer accepted.")
        if any(v.citizen_id == citizen_id for v in self.votes):
            raise ValueError(f"Citizen {citizen_id} has already voted on debate {self.debate_id}.")
        vote = Vote(debate_id=self.debate_id, citizen_id=citizen_id, choice=choice)
        self.votes.append(vote)
        return vote

    def close(self) -> None:
        """Close the debate to further voting."""
        if self.status != DebateStatus.OPEN:
            raise RuntimeError(f"Debate {self.debate_id} is already closed.")
        self.status = DebateStatus.CLOSED
        self.closed_at = datetime.now(timezone.utc)

    @property
    def tally(self) -> dict:
        """Return a vote tally for this debate."""
        result = {choice: 0 for choice in VoteChoice}
        for vote in self.votes:
            result[vote.choice] += 1
        return {c.value: count for c, count in result.items()}
