from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from math import floor
from random import Random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import AuditionEvent, AuditionSession
from app.schemas.audition import AuditionCreateRequest, AuditionEventRead, AuditionLiveState, AuditionSessionRead


@dataclass(frozen=True)
class ActionCandidate:
    action_type: str
    zone: str
    confidence: int
    stress: int
    camera_heat: int
    tags: tuple[str, ...]


BEAT_LIBRARY: list[list[ActionCandidate]] = [
    [
        ActionCandidate("enter_set", "entrance", 6, 3, 4, ("bold", "camera")),
        ActionCandidate("scan_room", "entrance", 2, 1, 1, ("analytical", "guarded")),
    ],
    [
        ActionCandidate("greet_host", "host_mark", 7, -1, 4, ("warm", "social")),
        ActionCandidate("offer_handshake", "host_mark", 4, -2, 2, ("precise", "calm")),
    ],
    [
        ActionCandidate("hit_mark", "spotlight", 5, 0, 5, ("camera", "disciplined")),
        ActionCandidate("play_to_cameras", "camera_lane", 7, 2, 8, ("theatrical", "chaotic")),
    ],
    [
        ActionCandidate("deliver_hook", "spotlight", 8, 1, 7, ("bold", "strategic")),
        ActionCandidate("reveal_soft_side", "confessional_cam", 5, 3, 4, ("warm", "vulnerable")),
    ],
    [
        ActionCandidate("improvise_bit", "camera_lane", 7, 2, 9, ("chaotic", "funny")),
        ActionCandidate("frame_backstory", "spotlight", 4, 1, 5, ("analytical", "composed")),
    ],
    [
        ActionCandidate("answer_pressure_question", "host_mark", 6, 4, 5, ("strategic", "calm")),
        ActionCandidate("challenge_the_prompt", "spotlight", 9, 6, 8, ("bold", "chaotic")),
    ],
    [
        ActionCandidate("walk_camera_lane", "camera_lane", 5, 1, 8, ("camera", "confident")),
        ActionCandidate("lock_in_eye_contact", "spotlight", 6, 0, 6, ("romantic", "soft")),
    ],
    [
        ActionCandidate("handle_awkward_pause", "spotlight", 4, 5, 4, ("shy", "guarded")),
        ActionCandidate("turn_pause_into_joke", "camera_lane", 8, 1, 7, ("funny", "chaotic")),
    ],
    [
        ActionCandidate("confessional_punch", "confessional_cam", 7, 2, 6, ("strategic", "vulnerable")),
        ActionCandidate("state_motive_cleanly", "confessional_cam", 5, 0, 4, ("analytical", "disciplined")),
    ],
    [
        ActionCandidate("close_with_tagline", "spotlight", 8, 1, 8, ("camera", "bold")),
        ActionCandidate("close_with_smirk", "exit_mark", 6, -1, 5, ("villain", "guarded")),
    ],
]

TRAIT_SCORES = {
    "bold": {"confidence": 3, "camera_heat": 2},
    "confident": {"confidence": 3, "camera_heat": 1},
    "warm": {"confidence": 1, "stress": -2},
    "empathetic": {"confidence": 1, "stress": -1},
    "chaotic": {"camera_heat": 3, "stress": 1},
    "strategic": {"confidence": 2},
    "analytical": {"confidence": 1, "stress": -1},
    "shy": {"confidence": -2, "stress": 2},
    "guarded": {"stress": 1},
    "funny": {"camera_heat": 2, "confidence": 1},
    "romantic": {"camera_heat": 1},
    "theatrical": {"camera_heat": 3, "confidence": 2},
    "calm": {"stress": -2},
}


def _stable_seed(payload: AuditionCreateRequest) -> int:
    material = "|".join(
        [
            payload.provider_config.provider,
            payload.provider_config.api_base_url or "",
            payload.provider_config.model_name,
            payload.agent_config.character_name,
            payload.agent_config.archetype,
            payload.agent_config.speech_style,
            payload.agent_config.public_hook,
            ",".join(payload.agent_config.traits),
            payload.agent_config.skin.palette,
            payload.agent_config.skin.accent,
            payload.agent_config.skin.silhouette,
            payload.agent_config.skin.hair_style,
            str(payload.simulated_minutes),
            str(payload.playback_ms_per_beat),
        ]
    )
    return int(sha256(material.encode("utf-8")).hexdigest()[:12], 16)


def _trait_vector(traits: list[str]) -> dict[str, int]:
    vector = {"confidence": 0, "stress": 0, "camera_heat": 0}
    for trait in traits:
        normalized = trait.strip().lower().replace(" ", "_")
        for key, value in TRAIT_SCORES.get(normalized, {}).items():
            vector[key] += value
    return vector


def _choose_candidate(rng: Random, archetype: str, traits: list[str], beat_index: int) -> ActionCandidate:
    candidates = BEAT_LIBRARY[min(beat_index, len(BEAT_LIBRARY) - 1)]
    vector = _trait_vector(traits + [archetype.lower()])

    def score(candidate: ActionCandidate) -> float:
        tag_bonus = sum(2 for tag in candidate.tags if tag in archetype.lower() or tag in " ".join(traits).lower())
        return (
            candidate.confidence
            + vector["confidence"]
            + candidate.camera_heat * 0.8
            - candidate.stress * 0.35
            + tag_bonus
            + rng.uniform(-1.1, 1.1)
        )

    return max(candidates, key=score)


def _dialogue_line(name: str, speech_style: str, action_type: str, public_hook: str, rng: Random) -> str:
    openers = {
        "enter_set": "I don't enter rooms quietly.",
        "greet_host": "Good evening, I'm here to leave a mark.",
        "offer_handshake": "Let's make this simple and sharp.",
        "deliver_hook": public_hook,
        "improvise_bit": "If the room blinks first, I win.",
        "answer_pressure_question": "Pressure is where personality stops pretending.",
        "challenge_the_prompt": "If this is a test, let's make it worth broadcasting.",
        "walk_camera_lane": "Find your lens, then own it.",
        "handle_awkward_pause": "Silence still tells on people.",
        "turn_pause_into_joke": "If the cue dies, I become the cue.",
        "confessional_punch": "What they call instinct is usually strategy with better lighting.",
        "state_motive_cleanly": "I want the room, the story, and the aftermath.",
        "close_with_tagline": "Cast me once and the house never stays calm again.",
        "close_with_smirk": "You won't forget the silhouette leaving the light.",
    }
    suffixes = [
        f" Delivered in a {speech_style.lower()} register.",
        " The camera read is immediate.",
        " The beat lands cleanly under the studio lights.",
    ]
    return f"{name}: {openers.get(action_type, public_hook)}{rng.choice(suffixes)}"


def _summary_line(name: str, candidate: ActionCandidate, beat_index: int) -> str:
    return (
        f"{name} hits beat {beat_index + 1} in the {candidate.zone.replace('_', ' ')} and "
        f"uses `{candidate.action_type}` to push the audition narrative forward."
    )


def _snapshot(confidence: float, stress: float, camera_heat: float) -> dict:
    return {
        "confidence": max(0, min(100, round(confidence))),
        "stress": max(0, min(100, round(stress))),
        "camera_heat": max(0, min(100, round(camera_heat))),
    }


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def create_audition_session(db: Session, payload: AuditionCreateRequest) -> AuditionSession:
    seed = _stable_seed(payload)
    rng = Random(seed)
    total_beats = max(8, payload.simulated_minutes * 2)
    started_at = datetime.now(timezone.utc)

    session = AuditionSession(
        status="running",
        environment_code="tv_audition_stage",
        environment_label="Neural House TV Audition Loft",
        provider=payload.provider_config.provider,
        api_base_url=payload.provider_config.api_base_url,
        model_name=payload.provider_config.model_name,
        provider_enabled=payload.provider_config.enabled,
        character_name=payload.agent_config.character_name,
        archetype=payload.agent_config.archetype,
        speech_style=payload.agent_config.speech_style,
        public_hook=payload.agent_config.public_hook,
        traits_json=payload.agent_config.traits,
        strengths_json=payload.agent_config.strengths,
        weaknesses_json=payload.agent_config.weaknesses,
        skin_palette=payload.agent_config.skin.palette,
        skin_accent=payload.agent_config.skin.accent,
        skin_silhouette=payload.agent_config.skin.silhouette,
        hair_style=payload.agent_config.skin.hair_style,
        simulated_minutes=payload.simulated_minutes,
        playback_ms_per_beat=payload.playback_ms_per_beat,
        total_beats=total_beats,
        current_beat=1,
        summary=(
            f"{payload.agent_config.character_name} is running a deterministic audition inside the Neural House loft. "
            f"Provider config is captured as {payload.provider_config.provider}/{payload.provider_config.model_name}; "
            f"behavior remains state-driven even when external model access is disabled."
        ),
        session_seed=seed,
        started_at=started_at,
        ended_at=None,
    )
    db.add(session)
    db.flush()

    trait_vector = _trait_vector(payload.agent_config.traits + [payload.agent_config.archetype.lower()])
    confidence = 54 + trait_vector["confidence"] * 2
    stress = 24 + trait_vector["stress"] * 2
    camera_heat = 42 + trait_vector["camera_heat"] * 2
    beat_seconds = max(15, floor((payload.simulated_minutes * 60) / total_beats))

    events: list[AuditionEvent] = []
    for beat_index in range(total_beats):
        candidate = _choose_candidate(rng, payload.agent_config.archetype, payload.agent_config.traits, beat_index)
        confidence += candidate.confidence * 0.7 + rng.uniform(-1.2, 1.8)
        stress += candidate.stress * 0.8 + rng.uniform(-0.8, 1.2)
        camera_heat += candidate.camera_heat * 0.6 + rng.uniform(-1.0, 1.5)
        event = AuditionEvent(
            session_id=session.id,
            tick_number=beat_index,
            simulated_second=beat_index * beat_seconds,
            zone=candidate.zone,
            action_type=candidate.action_type,
            summary=_summary_line(payload.agent_config.character_name, candidate, beat_index),
            dialogue=_dialogue_line(
                payload.agent_config.character_name,
                payload.agent_config.speech_style,
                candidate.action_type,
                payload.agent_config.public_hook,
                rng,
            ),
            state_snapshot_json=_snapshot(confidence, stress, camera_heat),
        )
        db.add(event)
        events.append(event)

    db.commit()
    db.refresh(session)
    return session


def _update_progress(db: Session, session: AuditionSession) -> AuditionSession:
    started_at = _as_utc(session.started_at)
    elapsed_ms = max(0, int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000))
    visible_beats = min(session.total_beats, floor(elapsed_ms / session.playback_ms_per_beat) + 1)
    status = "completed" if elapsed_ms >= session.playback_ms_per_beat * session.total_beats else "running"
    should_commit = False
    if session.current_beat != visible_beats:
        session.current_beat = visible_beats
        should_commit = True
    if session.status != status:
        session.status = status
        if status == "completed" and session.ended_at is None:
            session.ended_at = started_at + timedelta(milliseconds=session.playback_ms_per_beat * session.total_beats)
        should_commit = True
    if should_commit:
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def get_audition_session(db: Session, session_id: int) -> AuditionSession | None:
    session = db.get(AuditionSession, session_id)
    if session is None:
        return None
    return _update_progress(db, session)


def list_audition_sessions(db: Session) -> list[AuditionSession]:
    sessions = list(db.scalars(select(AuditionSession).order_by(AuditionSession.created_at.desc())))
    return [_update_progress(db, session) for session in sessions]


def list_audition_events(db: Session, session_id: int, visible_only: bool = False) -> list[AuditionEvent]:
    session = get_audition_session(db, session_id)
    if session is None:
        return []
    events = list(db.scalars(select(AuditionEvent).where(AuditionEvent.session_id == session_id).order_by(AuditionEvent.tick_number)))
    if visible_only:
        return [event for event in events if event.tick_number < session.current_beat]
    return events


def serialize_session(session: AuditionSession) -> AuditionSessionRead:
    return AuditionSessionRead(
        id=session.id,
        status=session.status,
        environment_code=session.environment_code,
        environment_label=session.environment_label,
        provider=session.provider,
        api_base_url=session.api_base_url,
        model_name=session.model_name,
        provider_enabled=session.provider_enabled,
        character_name=session.character_name,
        archetype=session.archetype,
        speech_style=session.speech_style,
        public_hook=session.public_hook,
        traits_json=session.traits_json,
        strengths_json=session.strengths_json,
        weaknesses_json=session.weaknesses_json,
        skin_palette=session.skin_palette,
        skin_accent=session.skin_accent,
        skin_silhouette=session.skin_silhouette,
        hair_style=session.hair_style,
        simulated_minutes=session.simulated_minutes,
        playback_ms_per_beat=session.playback_ms_per_beat,
        total_beats=session.total_beats,
        current_beat=session.current_beat,
        summary=session.summary,
        session_seed=session.session_seed,
        created_at=session.created_at,
        started_at=session.started_at,
        ended_at=session.ended_at,
    )


def serialize_event(event: AuditionEvent) -> AuditionEventRead:
    return AuditionEventRead(
        id=event.id,
        session_id=event.session_id,
        tick_number=event.tick_number,
        simulated_second=event.simulated_second,
        zone=event.zone,
        action_type=event.action_type,
        summary=event.summary,
        dialogue=event.dialogue,
        state_snapshot_json=event.state_snapshot_json,
        created_at=event.created_at,
    )


def get_live_state(db: Session, session_id: int) -> AuditionLiveState | None:
    session = get_audition_session(db, session_id)
    if session is None:
        return None
    visible_events = [serialize_event(event) for event in list_audition_events(db, session_id, visible_only=True)]
    next_eta_ms = None
    if session.status != "completed":
        started_at = _as_utc(session.started_at)
        elapsed_ms = max(0, int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000))
        next_eta_ms = session.playback_ms_per_beat - (elapsed_ms % session.playback_ms_per_beat)
    return AuditionLiveState(
        session=serialize_session(session),
        visible_events=visible_events,
        next_event_eta_ms=next_eta_ms,
    )
