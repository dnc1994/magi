import random
from magi.voting import VoteOutcome, generate_votes, VotingSession, COMPUTER_NAMES


def test_computer_names():
    assert COMPUTER_NAMES == ["MELCHIOR-1", "BALTHASAR-2", "CASPAR-3"]


def test_vote_outcome_values():
    assert VoteOutcome.APPROVED.value == "APPROVED"
    assert VoteOutcome.REJECTED.value == "REJECTED"


def test_generate_votes_returns_three():
    votes = generate_votes()
    assert len(votes) == 3


def test_generate_votes_all_valid():
    for _ in range(100):
        votes = generate_votes()
        assert all(v in (VoteOutcome.APPROVED, VoteOutcome.REJECTED) for v in votes)


def test_generate_votes_split_bias():
    """Over 500 trials, splits should be ~70% (allow ±15%)."""
    random.seed(42)
    splits = sum(1 for _ in range(500) if len(set(generate_votes())) > 1)
    assert 275 < splits < 425, f"Expected ~70% splits, got {splits}/500"


def test_voting_session_counts():
    session = VotingSession("INITIATE TEST")
    session.record_vote("MELCHIOR-1", VoteOutcome.APPROVED)
    session.record_vote("BALTHASAR-2", VoteOutcome.REJECTED)
    assert session.approved_count == 1
    assert session.rejected_count == 1
    assert not session.is_complete


def test_voting_session_complete():
    session = VotingSession("INITIATE TEST")
    for name in COMPUTER_NAMES:
        session.record_vote(name, VoteOutcome.APPROVED)
    assert session.is_complete
    assert session.approved_count == 3


def test_verdict_string_split_approved():
    session = VotingSession("TEST")
    session.record_vote("MELCHIOR-1", VoteOutcome.APPROVED)
    session.record_vote("BALTHASAR-2", VoteOutcome.APPROVED)
    session.record_vote("CASPAR-3", VoteOutcome.REJECTED)
    assert session.verdict_string() == "APPROVED (2–1)"


def test_verdict_string_split_rejected():
    session = VotingSession("TEST")
    session.record_vote("MELCHIOR-1", VoteOutcome.REJECTED)
    session.record_vote("BALTHASAR-2", VoteOutcome.REJECTED)
    session.record_vote("CASPAR-3", VoteOutcome.APPROVED)
    assert session.verdict_string() == "REJECTED (2–1)"


def test_verdict_string_unanimous_approval():
    session = VotingSession("TEST")
    for name in COMPUTER_NAMES:
        session.record_vote(name, VoteOutcome.APPROVED)
    assert session.verdict_string() == "UNANIMOUS APPROVAL"


def test_verdict_string_unanimous_rejection():
    session = VotingSession("TEST")
    for name in COMPUTER_NAMES:
        session.record_vote(name, VoteOutcome.REJECTED)
    assert session.verdict_string() == "UNANIMOUS REJECTION"
