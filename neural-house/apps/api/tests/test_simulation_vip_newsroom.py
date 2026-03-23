from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.models.entities import Journalist, PremiumUser


def _seed_vip_and_newsroom_support(
    sqlite_session_factory: sessionmaker[Session],
    season_id: int,
) -> tuple[int, list[int]]:
    db = sqlite_session_factory()
    try:
        premium_user = PremiumUser(
            email="vip-smoke@neural.house",
            display_name="VIP Smoke Viewer",
            premium_tier="founder",
            active=True,
        )
        journalists = [
            Journalist(
                season_id=season_id,
                display_name="Tara Volt",
                style="tabloid gossip",
                ideology="sensationalism-first",
                sensationalism=0.92,
                empathy=0.28,
                bias_profile_json={"lens": "dramatic"},
                activity_interval_ticks=4,
                active=True,
            ),
            Journalist(
                season_id=season_id,
                display_name="Nico Vale",
                style="serious analyst",
                ideology="structure-and-game",
                sensationalism=0.22,
                empathy=0.71,
                bias_profile_json={"lens": "analytical"},
                activity_interval_ticks=6,
                active=True,
            ),
            Journalist(
                season_id=season_id,
                display_name="Mila Rook",
                style="moralizing cultural critic",
                ideology="ethics-and-consequence",
                sensationalism=0.39,
                empathy=0.83,
                bias_profile_json={"lens": "moral"},
                activity_interval_ticks=8,
                active=True,
            ),
        ]
        db.add(premium_user)
        db.add_all(journalists)
        db.commit()
        db.refresh(premium_user)
        journalist_ids = [journalist.id for journalist in journalists]
        return premium_user.id, journalist_ids
    finally:
        db.close()


def _find_relationship(response_json: list[dict], source_id: int, target_id: int) -> dict:
    for relationship in response_json:
        if (
            relationship["source_contestant_id"] == source_id
            and relationship["target_contestant_id"] == target_id
        ):
            return relationship
    raise AssertionError(f"Relationship {source_id}->{target_id} not found")


def test_simulation_progression_updates_relationships_and_state(
    client,
    seeded_season: int,
) -> None:
    baseline_response = client.get(f"/api/seasons/{seeded_season}/relationships")
    assert baseline_response.status_code == 200
    baseline_relationships = baseline_response.json()
    assert baseline_relationships

    tick_response = client.post(f"/api/seasons/{seeded_season}/simulation/tick")
    assert tick_response.status_code == 200
    latest_event = tick_response.json()
    actor_ids = latest_event["payload_json"]["actor_ids"]
    assert len(actor_ids) >= 2

    state_response = client.get(f"/api/seasons/{seeded_season}/simulation/state")
    assert state_response.status_code == 200
    state = state_response.json()
    assert state["season_id"] == seeded_season
    assert state["tick_number"] == 1
    assert state["status"] == "running"
    assert len(state["recent_event_ids"]) == 1
    assert state["active_room_code"] in {"living_room", "kitchen", "garden", "bedroom", "confessional"}

    after_response = client.get(f"/api/seasons/{seeded_season}/relationships")
    assert after_response.status_code == 200
    after_relationships = after_response.json()

    before_forward = _find_relationship(baseline_relationships, actor_ids[0], actor_ids[1])
    after_forward = _find_relationship(after_relationships, actor_ids[0], actor_ids[1])
    before_reverse = _find_relationship(baseline_relationships, actor_ids[1], actor_ids[0])
    after_reverse = _find_relationship(after_relationships, actor_ids[1], actor_ids[0])

    forward_delta = latest_event["payload_json"]["relationship_delta"]["forward_delta"]
    reverse_delta = latest_event["payload_json"]["relationship_delta"]["reverse_delta"]
    forward_field = next(field for field, delta in forward_delta.items() if abs(delta) > 0)
    reverse_field = next(field for field, delta in reverse_delta.items() if abs(delta) > 0)

    assert after_forward[forward_field] != before_forward[forward_field]
    assert after_reverse[reverse_field] != before_reverse[reverse_field]
    assert after_forward["last_significant_change_at"] >= before_forward["last_significant_change_at"]
    assert after_reverse["last_significant_change_at"] >= before_reverse["last_significant_change_at"]


def test_newsroom_cycle_publishes_articles_from_latest_simulation_event(
    client,
    seeded_season: int,
    sqlite_session_factory,
) -> None:
    client.post(f"/api/seasons/{seeded_season}/simulation/start")
    tick_response = client.post(f"/api/seasons/{seeded_season}/simulation/tick")
    assert tick_response.status_code == 200
    latest_event = tick_response.json()
    expected_phrase = latest_event["event_type"].replace("_", " ")

    premium_user_id, journalist_ids = _seed_vip_and_newsroom_support(sqlite_session_factory, seeded_season)
    assert premium_user_id > 0
    assert len(journalist_ids) == 3

    cycle_response = client.post(f"/api/seasons/{seeded_season}/newsroom/run-cycle")
    assert cycle_response.status_code == 200
    cycle_result = cycle_response.json()
    assert len(cycle_result["published_article_ids"]) == 3

    articles_response = client.get(f"/api/seasons/{seeded_season}/articles")
    assert articles_response.status_code == 200
    articles = articles_response.json()
    assert len(articles) == 3
    assert {article["journalist_id"] for article in articles} == set(journalist_ids)
    assert all(expected_phrase in article["title"] for article in articles)
    assert all(article["body"].startswith("Deterministic fallback article") for article in articles)
    assert all(latest_event["id"] in article["referenced_event_ids_json"] for article in articles)
    assert {article["tone"] for article in articles} == {
        "tabloid gossip",
        "serious analyst",
        "moralizing cultural critic",
    }


def test_vip_state_and_session_track_live_house_progress(
    client,
    seeded_season: int,
    sqlite_session_factory,
) -> None:
    client.post(f"/api/seasons/{seeded_season}/simulation/start")
    first_tick_response = client.post(f"/api/seasons/{seeded_season}/simulation/tick")
    assert first_tick_response.status_code == 200
    first_event = first_tick_response.json()

    premium_user_id, _ = _seed_vip_and_newsroom_support(sqlite_session_factory, seeded_season)

    vip_state_response = client.get(
        f"/api/seasons/{seeded_season}/vip/state",
        params={"premium_user_id": premium_user_id, "selected_room_code": "garden"},
    )
    assert vip_state_response.status_code == 200
    vip_state = vip_state_response.json()
    assert vip_state["season_id"] == seeded_season
    assert vip_state["tick_number"] == first_event["tick_number"]
    assert vip_state["selected_room_code"] == "garden"
    assert len(vip_state["rooms"]) == 5
    assert vip_state["recent_events"]
    assert first_event["summary"] == vip_state["recent_events"][0]
    assert vip_state["tension"] >= 0

    start_session_response = client.post(
        f"/api/seasons/{seeded_season}/vip/session/start",
        json={"premium_user_id": premium_user_id, "selected_room_code": "garden"},
    )
    assert start_session_response.status_code == 200
    vip_session = start_session_response.json()
    assert vip_session["premium_user_id"] == premium_user_id
    assert vip_session["season_id"] == seeded_season
    assert vip_session["selected_room_code"] == "garden"
    assert vip_session["ended_at"] is None
    assert vip_session["session_meta_json"]["entry_mode"] == "debug_stub"

    end_session_response = client.post(
        f"/api/seasons/{seeded_season}/vip/session/end",
        params={"session_id": vip_session["id"]},
    )
    assert end_session_response.status_code == 200
    ended_session = end_session_response.json()
    assert ended_session["id"] == vip_session["id"]
    assert ended_session["ended_at"] is not None
