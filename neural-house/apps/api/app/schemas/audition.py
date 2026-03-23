from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AuditionProviderConfig(BaseModel):
    provider: str = "local_stub"
    api_base_url: str | None = None
    model_name: str = "deterministic-fallback"
    enabled: bool = False


class AuditionSkinConfig(BaseModel):
    palette: str = "studio_blue"
    accent: str = "gold"
    silhouette: str = "host-ready"
    hair_style: str = "crown"


class AuditionAgentConfig(BaseModel):
    character_name: str
    archetype: str
    speech_style: str
    public_hook: str
    traits: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    skin: AuditionSkinConfig = Field(default_factory=AuditionSkinConfig)


class AuditionCreateRequest(BaseModel):
    provider_config: AuditionProviderConfig = Field(default_factory=AuditionProviderConfig)
    agent_config: AuditionAgentConfig
    simulated_minutes: int = Field(default=6, ge=2, le=12)
    playback_ms_per_beat: int = Field(default=5000, ge=500, le=15000)


class AuditionEventRead(BaseModel):
    id: int
    session_id: int
    tick_number: int
    simulated_second: int
    zone: str
    action_type: str
    summary: str
    dialogue: str | None
    state_snapshot_json: dict
    created_at: datetime


class AuditionSessionRead(BaseModel):
    id: int
    status: str
    environment_code: str
    environment_label: str
    provider: str
    api_base_url: str | None
    model_name: str
    provider_enabled: bool
    character_name: str
    archetype: str
    speech_style: str
    public_hook: str
    traits_json: list[str]
    strengths_json: list[str]
    weaknesses_json: list[str]
    skin_palette: str
    skin_accent: str
    skin_silhouette: str
    hair_style: str
    simulated_minutes: int
    playback_ms_per_beat: int
    total_beats: int
    current_beat: int
    summary: str
    session_seed: int
    created_at: datetime
    started_at: datetime
    ended_at: datetime | None


class AuditionLiveState(BaseModel):
    session: AuditionSessionRead
    visible_events: list[AuditionEventRead]
    next_event_eta_ms: int | None
