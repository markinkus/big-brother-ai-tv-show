from enum import StrEnum


class AuditionRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditionExecutionMode(StrEnum):
    INLINE = "inline"
    QUEUED = "queued"


class AuditionLlmMode(StrEnum):
    DISABLED = "disabled"
    FALLBACK = "fallback"
    LIVE = "live"
