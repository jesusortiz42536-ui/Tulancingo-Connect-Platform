"""
Tests for the civic_forum (Denarytor) module.
"""

import pytest

from civic_forum.models import (
    Debate,
    DebateStatus,
    Report,
    ReportCategory,
    ReportStatus,
    VoteChoice,
)
from civic_forum.forum import CivicForum


# ---------------------------------------------------------------------------
# Report tests
# ---------------------------------------------------------------------------

class TestReport:
    def _make_report(self):
        return Report(
            title="Bache en calle principal",
            description="Hay un bache grande en Av. Morelos frente al mercado.",
            category=ReportCategory.INFRASTRUCTURE,
            location="Av. Morelos, Tulancingo",
            submitted_by="citizen-001",
        )

    def test_create_report(self):
        r = self._make_report()
        assert r.status == ReportStatus.SUBMITTED

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Report(
                title="  ",
                description="desc",
                category=ReportCategory.OTHER,
                location="loc",
                submitted_by="cid",
            )

    def test_lifecycle(self):
        r = self._make_report()
        r.start_review()
        assert r.status == ReportStatus.UNDER_REVIEW
        r.resolve()
        assert r.status == ReportStatus.RESOLVED

    def test_reject(self):
        r = self._make_report()
        r.reject(reason="Duplicate report")
        assert r.status == ReportStatus.REJECTED

    def test_reject_resolved_raises(self):
        r = self._make_report()
        r.resolve()
        with pytest.raises(RuntimeError):
            r.reject()


# ---------------------------------------------------------------------------
# Debate tests
# ---------------------------------------------------------------------------

class TestDebate:
    def _make_debate(self):
        return Debate(
            title="¿Debe ampliarse el parque central?",
            description="Propuesta para extender el área verde del parque central.",
            created_by="moderator-001",
        )

    def test_create_debate(self):
        d = self._make_debate()
        assert d.status == DebateStatus.OPEN
        assert d.tally == {"for": 0, "against": 0, "abstain": 0}

    def test_cast_vote(self):
        d = self._make_debate()
        d.cast_vote("citizen-1", VoteChoice.FOR)
        d.cast_vote("citizen-2", VoteChoice.FOR)
        d.cast_vote("citizen-3", VoteChoice.AGAINST)
        tally = d.tally
        assert tally["for"] == 2
        assert tally["against"] == 1

    def test_duplicate_vote_raises(self):
        d = self._make_debate()
        d.cast_vote("citizen-1", VoteChoice.FOR)
        with pytest.raises(ValueError):
            d.cast_vote("citizen-1", VoteChoice.AGAINST)

    def test_vote_on_closed_debate_raises(self):
        d = self._make_debate()
        d.close()
        with pytest.raises(RuntimeError):
            d.cast_vote("citizen-1", VoteChoice.FOR)

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Debate(title=" ", description="desc", created_by="mod")


# ---------------------------------------------------------------------------
# CivicForum integration tests
# ---------------------------------------------------------------------------

class TestCivicForum:
    def test_submit_and_resolve_report(self):
        forum = CivicForum()
        report = forum.submit_report(
            title="Alumbrado apagado",
            description="La calle Hidalgo está a oscuras desde hace tres días.",
            category=ReportCategory.INFRASTRUCTURE,
            location="Calle Hidalgo, Tulancingo",
            submitted_by="citizen-abc",
        )
        forum.review_report(report.report_id)
        forum.resolve_report(report.report_id)
        assert report.status == ReportStatus.RESOLVED

    def test_open_debate_and_vote(self):
        forum = CivicForum()
        debate = forum.open_debate(
            title="Nueva ciclovía en Blvd. Valle",
            description="¿Debe construirse una ciclovía en el Blvd. Valle?",
            created_by="authority-001",
        )
        forum.vote_on_debate(debate.debate_id, "c-1", VoteChoice.FOR)
        forum.vote_on_debate(debate.debate_id, "c-2", VoteChoice.AGAINST)
        forum.close_debate(debate.debate_id)
        assert debate.status == DebateStatus.CLOSED
        assert debate.tally["for"] == 1

    def test_list_reports_filtered_by_status(self):
        forum = CivicForum()
        forum.submit_report("R1", "desc1", ReportCategory.OTHER, "loc", "u1")
        r2 = forum.submit_report("R2", "desc2", ReportCategory.HEALTH, "loc", "u2")
        forum.resolve_report(r2.report_id)
        open_reports = forum.list_reports(status=ReportStatus.SUBMITTED)
        resolved_reports = forum.list_reports(status=ReportStatus.RESOLVED)
        assert len(open_reports) == 1
        assert len(resolved_reports) == 1

    def test_get_nonexistent_report_raises(self):
        forum = CivicForum()
        with pytest.raises(KeyError):
            forum.get_report("nonexistent-id")
