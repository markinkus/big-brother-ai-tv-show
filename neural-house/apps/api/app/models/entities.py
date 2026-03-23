from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampedMixin, UpdatedTimestampedMixin


class Season(UpdatedTimestampedMixin, Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    seed: Mapped[int] = mapped_column(Integer)

    rooms: Mapped[list["Room"]] = relationship(back_populates="season", cascade="all, delete-orphan")
    contestants: Mapped[list["Contestant"]] = relationship(back_populates="season", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(120))
    x: Mapped[int] = mapped_column(Integer)
    y: Mapped[int] = mapped_column(Integer)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)

    season: Mapped["Season"] = relationship(back_populates="rooms")


class Contestant(TimestampedMixin, Base):
    __tablename__ = "contestants"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    display_name: Mapped[str] = mapped_column(String(120))
    archetype: Mapped[str] = mapped_column(String(80))
    avatar_seed: Mapped[int] = mapped_column(Integer, default=0)
    skin_palette: Mapped[str] = mapped_column(String(40), default="studio_blue")
    skin_accent: Mapped[str] = mapped_column(String(40), default="gold")
    skin_silhouette: Mapped[str] = mapped_column(String(40), default="host-ready")
    hair_style: Mapped[str] = mapped_column(String(40), default="crown")
    public_bio: Mapped[str] = mapped_column(Text)
    public_goal: Mapped[str] = mapped_column(Text)
    hidden_goal_summary: Mapped[str] = mapped_column(Text)
    speech_style: Mapped[str] = mapped_column(String(120))
    persona_card_id: Mapped[int | None] = mapped_column(ForeignKey("persona_cards.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    season: Mapped["Season"] = relationship(back_populates="contestants")


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    source_contestant_id: Mapped[int] = mapped_column(ForeignKey("contestants.id", ondelete="CASCADE"))
    target_contestant_id: Mapped[int] = mapped_column(ForeignKey("contestants.id", ondelete="CASCADE"))
    trust: Mapped[float] = mapped_column(Float, default=50.0)
    attraction: Mapped[float] = mapped_column(Float, default=15.0)
    rivalry: Mapped[float] = mapped_column(Float, default=18.0)
    fear: Mapped[float] = mapped_column(Float, default=10.0)
    respect: Mapped[float] = mapped_column(Float, default=40.0)
    manipulation: Mapped[float] = mapped_column(Float, default=12.0)
    familiarity: Mapped[float] = mapped_column(Float, default=20.0)
    last_significant_change_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ContestantState(UpdatedTimestampedMixin, Base):
    __tablename__ = "contestant_states"

    contestant_id: Mapped[int] = mapped_column(ForeignKey("contestants.id", ondelete="CASCADE"), primary_key=True)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    energy: Mapped[float] = mapped_column(Float, default=70.0)
    stress: Mapped[float] = mapped_column(Float, default=24.0)
    suspicion: Mapped[float] = mapped_column(Float, default=18.0)
    trust_baseline: Mapped[float] = mapped_column(Float, default=50.0)
    loneliness: Mapped[float] = mapped_column(Float, default=22.0)
    ambition: Mapped[float] = mapped_column(Float, default=55.0)
    confidence: Mapped[float] = mapped_column(Float, default=52.0)
    social_visibility: Mapped[float] = mapped_column(Float, default=26.0)
    current_focus: Mapped[str] = mapped_column(String(120), default="settling_in")
    status_effects_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Objective(UpdatedTimestampedMixin, Base):
    __tablename__ = "objectives"

    id: Mapped[int] = mapped_column(primary_key=True)
    contestant_id: Mapped[int] = mapped_column(ForeignKey("contestants.id", ondelete="CASCADE"))
    objective_type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[float] = mapped_column(Float, default=50.0)
    duration_ticks: Mapped[int] = mapped_column(Integer, default=24)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    success_conditions_json: Mapped[dict] = mapped_column(JSON, default=dict)
    failure_conditions_json: Mapped[dict] = mapped_column(JSON, default=dict)
    reward_json: Mapped[dict] = mapped_column(JSON, default=dict)
    penalty_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Memory(UpdatedTimestampedMixin, Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    contestant_id: Mapped[int] = mapped_column(ForeignKey("contestants.id", ondelete="CASCADE"))
    memory_type: Mapped[str] = mapped_column(String(40))
    summary: Mapped[str] = mapped_column(Text)
    salience: Mapped[float] = mapped_column(Float, default=0.0)
    emotional_valence: Mapped[float] = mapped_column(Float, default=0.0)
    strategic_value: Mapped[float] = mapped_column(Float, default=0.0)
    related_contestant_ids_json: Mapped[list[int]] = mapped_column(JSON, default=list)
    related_event_id: Mapped[int | None] = mapped_column(ForeignKey("simulation_events.id"), nullable=True)
    decay_rate: Mapped[float] = mapped_column(Float, default=0.15)


class Confessional(TimestampedMixin, Base):
    __tablename__ = "confessionals"

    id: Mapped[int] = mapped_column(primary_key=True)
    contestant_id: Mapped[int] = mapped_column(ForeignKey("contestants.id", ondelete="CASCADE"))
    triggered_by_event_id: Mapped[int | None] = mapped_column(ForeignKey("simulation_events.id"), nullable=True)
    public_transcript: Mapped[str] = mapped_column(Text)
    private_analysis: Mapped[str] = mapped_column(Text)
    shadow_flags_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    contradiction_flags_json: Mapped[list[str]] = mapped_column(JSON, default=list)


class Highlight(TimestampedMixin, Base):
    __tablename__ = "highlights"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey("simulation_events.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(180))
    summary: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float, default=0.0)


class PersonaCard(TimestampedMixin, Base):
    __tablename__ = "persona_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(50), default="candidate")
    base_seed: Mapped[int] = mapped_column(Integer)
    dominant_archetype: Mapped[str] = mapped_column(String(80))
    synopsis: Mapped[str] = mapped_column(Text)
    public_pitch: Mapped[str] = mapped_column(Text)
    private_complexity_summary: Mapped[str] = mapped_column(Text)
    trustability_score: Mapped[float] = mapped_column(Float)
    manipulation_susceptibility: Mapped[float] = mapped_column(Float)
    generation_notes_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Journalist(Base):
    __tablename__ = "journalists"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    display_name: Mapped[str] = mapped_column(String(120))
    style: Mapped[str] = mapped_column(String(80))
    ideology: Mapped[str] = mapped_column(String(120))
    sensationalism: Mapped[float] = mapped_column(Float)
    empathy: Mapped[float] = mapped_column(Float)
    bias_profile_json: Mapped[dict] = mapped_column(JSON, default=dict)
    activity_interval_ticks: Mapped[int] = mapped_column(Integer, default=12)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class SimulationEvent(TimestampedMixin, Base):
    __tablename__ = "simulation_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    tick_number: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(80))
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    summary: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    tension_score: Mapped[float] = mapped_column(Float, default=0.0)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    journalist_id: Mapped[int] = mapped_column(ForeignKey("journalists.id"))
    title: Mapped[str] = mapped_column(String(255))
    dek: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    tone: Mapped[str] = mapped_column(String(80))
    stance: Mapped[str] = mapped_column(String(80))
    referenced_event_ids_json: Mapped[list[int]] = mapped_column(JSON, default=list)
    referenced_contestant_ids_json: Mapped[list[int]] = mapped_column(JSON, default=list)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    visibility_scope: Mapped[str] = mapped_column(String(50), default="public")


class PremiumUser(TimestampedMixin, Base):
    __tablename__ = "premium_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    display_name: Mapped[str] = mapped_column(String(120))
    premium_tier: Mapped[str] = mapped_column(String(50))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class VipAccessSession(Base):
    __tablename__ = "vip_access_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    premium_user_id: Mapped[int] = mapped_column(ForeignKey("premium_users.id", ondelete="CASCADE"))
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    selected_room_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    session_meta_json: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditionSession(TimestampedMixin, Base):
    __tablename__ = "audition_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(40), default="running")
    environment_code: Mapped[str] = mapped_column(String(80), default="tv_audition_stage")
    environment_label: Mapped[str] = mapped_column(String(120), default="Neural House TV Audition Loft")
    provider: Mapped[str] = mapped_column(String(80), default="local_stub")
    api_base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_name: Mapped[str] = mapped_column(String(160), default="deterministic-fallback")
    provider_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    character_name: Mapped[str] = mapped_column(String(120))
    archetype: Mapped[str] = mapped_column(String(80))
    speech_style: Mapped[str] = mapped_column(String(160))
    public_hook: Mapped[str] = mapped_column(Text)
    traits_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    strengths_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    weaknesses_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    skin_palette: Mapped[str] = mapped_column(String(40), default="studio_blue")
    skin_accent: Mapped[str] = mapped_column(String(40), default="gold")
    skin_silhouette: Mapped[str] = mapped_column(String(40), default="host-ready")
    hair_style: Mapped[str] = mapped_column(String(40), default="crown")
    simulated_minutes: Mapped[int] = mapped_column(Integer, default=6)
    playback_ms_per_beat: Mapped[int] = mapped_column(Integer, default=5000)
    total_beats: Mapped[int] = mapped_column(Integer, default=12)
    current_beat: Mapped[int] = mapped_column(Integer, default=1)
    summary: Mapped[str] = mapped_column(Text)
    session_seed: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    events: Mapped[list["AuditionEvent"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="AuditionEvent.tick_number",
    )


class AuditionEvent(TimestampedMixin, Base):
    __tablename__ = "audition_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("audition_sessions.id", ondelete="CASCADE"))
    tick_number: Mapped[int] = mapped_column(Integer)
    simulated_second: Mapped[int] = mapped_column(Integer)
    zone: Mapped[str] = mapped_column(String(80))
    action_type: Mapped[str] = mapped_column(String(80))
    summary: Mapped[str] = mapped_column(Text)
    dialogue: Mapped[str | None] = mapped_column(Text, nullable=True)
    state_snapshot_json: Mapped[dict] = mapped_column(JSON, default=dict)

    session: Mapped["AuditionSession"] = relationship(back_populates="events")
