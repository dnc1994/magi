from magi.proposals import PROPOSALS, ProposalCycler


def test_at_least_15_proposals():
    assert len(PROPOSALS) >= 15


def test_proposals_are_uppercase():
    for p in PROPOSALS:
        assert p == p.upper(), f"{p!r} should be uppercase"


def test_proposals_are_nonempty():
    for p in PROPOSALS:
        assert p.strip(), "Proposal must not be blank"


def test_cycler_starts_at_first():
    cycler = ProposalCycler()
    assert cycler.next() == PROPOSALS[0]
    assert cycler.next() == PROPOSALS[1]


def test_cycler_wraps_around():
    cycler = ProposalCycler()
    seen = set()
    # Cycle through all + 1 to verify wrap
    for _ in range(len(PROPOSALS) + 1):
        seen.add(cycler.next())
    assert seen == set(PROPOSALS)
