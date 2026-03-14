from __future__ import annotations
import random
from dataclasses import dataclass, field
from enum import Enum

COMPUTER_NAMES: list[str] = ["MELCHIOR-1", "BALTHASAR-2", "CASPAR-3"]


class VoteOutcome(Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def generate_votes() -> list[VoteOutcome]:
    """Return 3 outcomes. ~30% unanimous, ~70% split (2-1)."""
    if random.random() < 0.30:
        outcome = random.choice(list(VoteOutcome))
        return [outcome, outcome, outcome]
    # Split 2-1
    if random.random() < 0.5:
        outcomes = [VoteOutcome.APPROVED, VoteOutcome.APPROVED, VoteOutcome.REJECTED]
    else:
        outcomes = [VoteOutcome.APPROVED, VoteOutcome.REJECTED, VoteOutcome.REJECTED]
    random.shuffle(outcomes)
    return outcomes


@dataclass
class VotingSession:
    proposal: str
    _votes: dict[str, VoteOutcome] = field(default_factory=dict, init=False)

    def record_vote(self, computer_name: str, outcome: VoteOutcome) -> None:
        self._votes[computer_name] = outcome

    @property
    def approved_count(self) -> int:
        return sum(1 for v in self._votes.values() if v == VoteOutcome.APPROVED)

    @property
    def rejected_count(self) -> int:
        return sum(1 for v in self._votes.values() if v == VoteOutcome.REJECTED)

    @property
    def is_complete(self) -> bool:
        return len(self._votes) == len(COMPUTER_NAMES)

    def verdict_string(self) -> str:
        a, r = self.approved_count, self.rejected_count
        if a == 3:
            return "UNANIMOUS APPROVAL"
        if r == 3:
            return "UNANIMOUS REJECTION"
        if a > r:
            return f"APPROVED ({a}–{r})"
        return f"REJECTED ({r}–{a})"
