from __future__ import annotations

from typing import Any


def test_create_audition_and_fetch_live_state(client) -> None:
    payload: dict[str, Any] = {
        "provider_config": {
            "provider": "openai_compatible",
            "api_base_url": "http://localhost:11434/v1",
            "model_name": "neural-house-smoke",
            "enabled": True,
        },
        "agent_config": {
            "character_name": "Ari",
            "archetype": "Chaotic",
            "speech_style": "sharp and playful",
            "public_hook": "I came here to turn the audition into television.",
            "traits": ["chaotic", "bold", "funny"],
            "strengths": ["camera instinct", "timing"],
            "weaknesses": ["impulsiveness"],
            "skin": {
                "palette": "neon-ink",
                "accent": "amber",
                "silhouette": "lean",
            },
        },
        "simulated_minutes": 4,
        "playback_ms_per_beat": 1000,
    }

    response = client.post("/api/auditions", json=payload)
    assert response.status_code == 200
    audition = response.json()
    assert audition["character_name"] == "Ari"
    assert audition["provider"] == "openai_compatible"
    assert audition["provider_enabled"] is True
    assert audition["skin_palette"] == "neon-ink"

    live_response = client.get(f"/api/auditions/{audition['id']}/live")
    assert live_response.status_code == 200
    live_state = live_response.json()
    assert live_state["session"]["id"] == audition["id"]
    assert live_state["session"]["character_name"] == "Ari"
    assert live_state["visible_events"]
    assert live_state["visible_events"][0]["action_type"] == "enter_set"
    assert live_state["next_event_eta_ms"] is not None


def test_start_tick_and_fetch_simulation_state(client, seeded_season: int) -> None:
    start_response = client.post(f"/api/seasons/{seeded_season}/simulation/start")
    assert start_response.status_code == 200
    start_state = start_response.json()
    assert start_state["season_id"] == seeded_season
    assert start_state["status"] == "running"
    assert start_state["tick_number"] == 0

    tick_response = client.post(f"/api/seasons/{seeded_season}/simulation/tick")
    assert tick_response.status_code == 200
    tick_event = tick_response.json()
    assert tick_event["season_id"] == seeded_season
    assert tick_event["tick_number"] == 1
    assert tick_event["event_type"]
    assert tick_event["summary"]

    state_response = client.get(f"/api/seasons/{seeded_season}/simulation/state")
    assert state_response.status_code == 200
    state = state_response.json()
    assert state["season_id"] == seeded_season
    assert state["status"] == "running"
    assert state["tick_number"] == 1
    assert state["active_room_code"] in {"living_room", "kitchen", "garden", "bedroom", "confessional"}
    assert state["recent_event_ids"]

    relationships_response = client.get(f"/api/seasons/{seeded_season}/relationships")
    assert relationships_response.status_code == 200
    relationships = relationships_response.json()
    assert relationships
    assert relationships[0]["source_name"]
    assert relationships[0]["target_name"]
    assert 0 <= relationships[0]["trust"] <= 100
