from enum import StrEnum


class ContestantStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    EVICTED = "evicted"
    WINNER = "winner"
