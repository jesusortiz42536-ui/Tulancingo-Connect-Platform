"""
CivicForum — central manager for Denarytor community engagement.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import Debate, DebateStatus, Report, ReportCategory, ReportStatus, Vote, VoteChoice


class CivicForum:
    """
    Manages public reports and community debates for Tulancingo citizens.

    Usage::

        forum = CivicForum()
        report = forum.submit_report(
            title="Broken streetlight",
            description="The streetlight on Av. Hidalgo has been out for a week.",
            category=ReportCategory.INFRASTRUCTURE,
            location="Av. Hidalgo, Tulancingo",
            submitted_by="citizen-uuid",
        )
    """

    def __init__(self) -> None:
        self._reports: Dict[str, Report] = {}
        self._debates: Dict[str, Debate] = {}

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def submit_report(
        self,
        title: str,
        description: str,
        category: ReportCategory,
        location: str,
        submitted_by: str,
    ) -> Report:
        """Submit a new public report."""
        report = Report(
            title=title,
            description=description,
            category=category,
            location=location,
            submitted_by=submitted_by,
        )
        self._reports[report.report_id] = report
        return report

    def get_report(self, report_id: str) -> Report:
        """Retrieve a report by ID."""
        try:
            return self._reports[report_id]
        except KeyError:
            raise KeyError(f"Report '{report_id}' not found.") from None

    def list_reports(self, status: Optional[ReportStatus] = None) -> List[Report]:
        """Return all reports, optionally filtered by status."""
        reports = list(self._reports.values())
        if status is not None:
            reports = [r for r in reports if r.status == status]
        return reports

    def review_report(self, report_id: str) -> Report:
        """Move a report to UNDER_REVIEW status."""
        report = self.get_report(report_id)
        report.start_review()
        return report

    def resolve_report(self, report_id: str) -> Report:
        """Mark a report as RESOLVED."""
        report = self.get_report(report_id)
        report.resolve()
        return report

    def reject_report(self, report_id: str, reason: str = "") -> Report:
        """Reject a report."""
        report = self.get_report(report_id)
        report.reject(reason)
        return report

    # ------------------------------------------------------------------
    # Debates
    # ------------------------------------------------------------------

    def open_debate(self, title: str, description: str, created_by: str) -> Debate:
        """Open a new community debate."""
        debate = Debate(title=title, description=description, created_by=created_by)
        self._debates[debate.debate_id] = debate
        return debate

    def get_debate(self, debate_id: str) -> Debate:
        """Retrieve a debate by ID."""
        try:
            return self._debates[debate_id]
        except KeyError:
            raise KeyError(f"Debate '{debate_id}' not found.") from None

    def list_debates(self, status: Optional[DebateStatus] = None) -> List[Debate]:
        """Return all debates, optionally filtered by status."""
        debates = list(self._debates.values())
        if status is not None:
            debates = [d for d in debates if d.status == status]
        return debates

    def vote_on_debate(self, debate_id: str, citizen_id: str, choice: VoteChoice) -> Vote:
        """Cast a citizen vote on a debate."""
        debate = self.get_debate(debate_id)
        return debate.cast_vote(citizen_id=citizen_id, choice=choice)

    def close_debate(self, debate_id: str) -> Debate:
        """Close a debate to further voting."""
        debate = self.get_debate(debate_id)
        debate.close()
        return debate
