from __future__ import annotations


def _run_first_tick(client, season_id: int) -> dict:
    start_response = client.post(f"/api/seasons/{season_id}/simulation/start")
    assert start_response.status_code == 200

    tick_response = client.post(f"/api/seasons/{season_id}/simulation/tick")
    assert tick_response.status_code == 200
    return tick_response.json()


def test_core_layer_endpoints_expose_state_objectives_memories_highlights_and_confessionals(
    client,
    seeded_season: int,
) -> None:
    latest_event = _run_first_tick(client, seeded_season)
    actor_ids = latest_event["payload_json"]["actor_ids"]
    assert len(actor_ids) >= 2
    assert latest_event["payload_json"]["memory_ids"]
    assert latest_event["payload_json"]["confessional_ids"]
    assert latest_event["payload_json"]["highlight_id"]
    assert latest_event["payload_json"]["objective_updates"]
    assert latest_event["payload_json"]["state_changes"]

    states_response = client.get(f"/api/seasons/{seeded_season}/contestant-states")
    assert states_response.status_code == 200
    states = states_response.json()
    assert len(states) == 3
    assert {state["display_name"] for state in states} == {"Mara", "Rico", "Lea"}
    assert all(state["room_code"] in {"living_room", "kitchen", "garden", "bedroom", "confessional"} for state in states)
    assert all("popularity" in state["status_effects_json"] for state in states)
    assert all("public_appeal" in state["status_effects_json"]["popularity"] for state in states)

    objectives_response = client.get(f"/api/seasons/{seeded_season}/objectives")
    assert objectives_response.status_code == 200
    objectives = objectives_response.json()
    assert len(objectives) >= 6
    assert {objective["contestant_name"] for objective in objectives} == {"Mara", "Rico", "Lea"}
    assert any(objective["progress"] > 0 for objective in objectives)
    assert all(objective["active"] in {True, False} for objective in objectives)

    memories_response = client.get(f"/api/seasons/{seeded_season}/memories")
    assert memories_response.status_code == 200
    memories = memories_response.json()
    assert memories
    assert {memory["contestant_name"] for memory in memories}.issubset({"Mara", "Rico", "Lea"})
    assert all(0.0 <= memory["salience"] <= 1.0 for memory in memories)
    assert all(memory["memory_type"] in {"working", "episodic", "core", "secret", "archive"} for memory in memories)
    assert all(memory["related_event_id"] is not None for memory in memories)

    highlights_response = client.get(f"/api/seasons/{seeded_season}/highlights")
    assert highlights_response.status_code == 200
    highlights = highlights_response.json()
    assert highlights
    assert {highlight["category"] for highlight in highlights}.issubset(
        {"conflict", "alliance", "romance", "contradiction", "confession", "challenge"}
    )
    assert all(0.0 <= highlight["score"] <= 1.0 for highlight in highlights)
    assert all(highlight["event_id"] == latest_event["id"] for highlight in highlights[:1])

    confessionals_response = client.get(f"/api/seasons/{seeded_season}/confessionals")
    assert confessionals_response.status_code == 200
    confessionals = confessionals_response.json()
    assert confessionals
    assert all(confessional["triggered_by_event_id"] is not None for confessional in confessionals)
    assert all(confessional["public_transcript"] for confessional in confessionals)
    assert all(confessional["private_analysis"] for confessional in confessionals)
    assert all(isinstance(confessional["shadow_flags_json"], list) for confessional in confessionals)
    assert all(isinstance(confessional["contradiction_flags_json"], list) for confessional in confessionals)


def test_weekly_live_surfaces_highlights_confessionals_and_persists_show_event(
    client,
    seeded_season: int,
) -> None:
    _run_first_tick(client, seeded_season)

    latest_response = client.get(f"/api/seasons/{seeded_season}/live/latest")
    assert latest_response.status_code == 200
    latest_live = latest_response.json()
    assert latest_live["season_id"] == seeded_season
    assert latest_live["tick_number"] == 1
    assert latest_live["segments"]
    assert latest_live["audience_pulse"]
    assert len(latest_live["audience_pulse"]) == 4
    assert len(latest_live["commentator_panels"]) >= 2
    assert any(segment["slot"] == "highlight_reveal" for segment in latest_live["segments"])
    assert any(segment["slot"] == "contradiction_reveal" for segment in latest_live["segments"])
    assert latest_live["scoreboard"]

    live_response = client.post(f"/api/seasons/{seeded_season}/live/run-weekly-show")
    assert live_response.status_code == 200
    weekly_live = live_response.json()
    assert weekly_live["season_id"] == seeded_season
    assert weekly_live["segments"]
    assert weekly_live["scoreboard"]
    assert any(segment["slot"] == "intro" for segment in weekly_live["segments"])
    assert any(segment["slot"] == "highlight_reveal" for segment in weekly_live["segments"])
    assert any(segment["slot"] == "contradiction_reveal" for segment in weekly_live["segments"])

    events_response = client.get(f"/api/seasons/{seeded_season}/events")
    assert events_response.status_code == 200
    events = events_response.json()
    assert any(event["event_type"] == "weekly_live_run" for event in events)
