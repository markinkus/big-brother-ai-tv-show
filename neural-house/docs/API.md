# API

Implemented endpoints in the current integrated MVP foundation:

- `GET /health`
- `GET /api/seasons`
- `POST /api/seasons`
- `GET /api/seasons/{season_id}`
- `GET /api/seasons/{season_id}/rooms`
- `GET /api/seasons/{season_id}/events`
- `GET /api/seasons/{season_id}/relationships`
- `GET /api/seasons/{season_id}/contestant-states`
- `GET /api/seasons/{season_id}/objectives`
- `GET /api/seasons/{season_id}/memories`
- `GET /api/seasons/{season_id}/highlights`
- `GET /api/seasons/{season_id}/confessionals`
- `GET /api/seasons/{season_id}/simulation/state`
- `POST /api/seasons/{season_id}/simulation/start`
- `POST /api/seasons/{season_id}/simulation/pause`
- `POST /api/seasons/{season_id}/simulation/resume`
- `POST /api/seasons/{season_id}/simulation/tick`
- `POST /api/seasons/{season_id}/simulation/ticks/{count}`
- `GET /api/seasons/{season_id}/contestants`
- `POST /api/seasons/{season_id}/contestants`
- `GET /api/contestants/{contestant_id}`
- `PATCH /api/contestants/{contestant_id}`
- `GET /api/seasons/{season_id}/persona-cards`
- `POST /api/seasons/{season_id}/persona-cards/generate`
- `GET /api/persona-cards/{persona_card_id}`
- `POST /api/persona-cards/{persona_card_id}/approve`
- `POST /api/persona-cards/{persona_card_id}/create-contestant`
- `GET /api/seasons/{season_id}/journalists`
- `GET /api/seasons/{season_id}/articles`
- `GET /api/articles/{article_id}`
- `POST /api/seasons/{season_id}/newsroom/run-cycle`
- `GET /api/seasons/{season_id}/vip/state`
- `GET /api/seasons/{season_id}/vip/rooms/{room_code}`
- `POST /api/seasons/{season_id}/vip/session/start`
- `POST /api/seasons/{season_id}/vip/session/end`
- `GET /api/seasons/{season_id}/live/latest`
- `POST /api/seasons/{season_id}/live/run-weekly-show`
- `GET /api/auditions`
- `POST /api/auditions`
- `GET /api/auditions/{session_id}`
- `GET /api/auditions/{session_id}/events`
- `GET /api/auditions/{session_id}/live`
- `WS /ws/seasons/{season_id}`

Core simulation notes:

- Simulation is still deterministic and seed-driven, but each tick now also persists contestant state changes, objective progress, memory records, confessionals, and highlight cards.
- The House Director can inject pacing beats such as rumor drops, truth/lie tests, trust tests, and forced dinner beats when the recent rhythm stagnates or overheats.
- VIP and newsroom now read persisted highlights, confessionals, relationship pressure, and room summaries instead of only the last raw event.
- Weekly live currently generates a structured studio pack from highlights, confessionals, articles, and tension pairs; it does not yet include full nominations or televote persistence.
- The audition/provino flow remains a separate state-driven stage that captures provider configuration without making world-state correctness depend on freeform model output.
