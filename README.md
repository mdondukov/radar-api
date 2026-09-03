# radar-api

Backend for the "radar" product family — self-assessment questionnaires
scored across several indicators and visualized as a radar chart. Replaces
the previous Kotlin/Spring `calc` service and is built so that a single
backend can serve several independent radar frontends off one deployment,
distinguished only by `project_code`:

- `calc-web` (deployed at `radar.biom.kg`) serves project `zhashyl-climate`
  — "Жашыл климат".
- `radar-women` (deployed at `radar-women.biom.kg`, a separate frontend
  repo cloned from `calc-web` and re-themed) serves project
  `fergana-women` — "Женщины Ферганы".

Both frontends call this same API instance (`https://radar.biom.kg/radar/`)
cross-origin, so `RADAR_CORS_ORIGINS` in production must list every
frontend's own domain, not just the one the API happens to be path-mounted
under.

## Stack

FastAPI + SQLAlchemy 2.0 (async) + asyncpg + Alembic + Pydantic v2.
Tooling: `uv` (deps/venv), `ruff` (lint), `mypy --strict` (types), `pytest` +
`pytest-asyncio` (tests).

## Domain model

The same generic set of entities serves any radar questionnaire:

```
project        — top-level radar (code, name, default_locale)
step           — a step of the flow: REGION | ASSESSMENT | RADAR, belongs to a project
region / area  — geo reference data (not every radar needs it; a REGION step is
                 simply omitted for projects that don't)
question       — belongs to a step
answer         — an answer option; carries a weight and an optional recommendation text
indicator      — one radar axis: 1:1 with an ASSESSMENT step (indicator.step_id)
```

Translatable fields (`name`, `content`, `descr`, `recommendation`, `impact`,
risk texts) are stored as `JSONB` — `{"ru": "...", "ky": "..."}` — and
resolved in the service layer (`app/services/i18n.py`) with a fallback to
`project.default_locale`. This is a deliberate departure from the original
Kotlin schema, where translations lived in separate `*_lang` tables using
`hstore` and were resolved by Postgres functions (`calc.step(_lang)` and so
on) — that approach worked, but porting stored SQL functions to the new
stack wasn't worth it: JSONB plus a Python fallback is easier to debug and
test outside the database.

### Indicator scoring

An indicator's value is the flat average `weight` of every selected answer
whose `AnswerSelect.step_id == indicator.step_id` (no intermediate averaging
per question). This is the exact formula the original `IndicatorService.calcValue`
used — unchanged in the port.

The risk zone is driven by thresholds configurable **per indicator**
(`indicator.high_risk_max`, `indicator.medium_risk_max`), not a global
constant: `value <= high_risk_max` → high, else `<= medium_risk_max` →
medium, else low. That lets different radars use different scales (not just
0–3) without touching code.

## Multi-tenancy and API

A radar is identified by a path segment: `/v1/{project_code}/poll/...`.
That's deliberately a path parameter rather than a header (like `locale`) —
it names a resource, not a presentation setting, so it's easier to scope
CORS per origin, log, and cache per project.

```
GET  /v1/{project_code}/poll/steps
GET  /v1/{project_code}/poll/regions
GET  /v1/{project_code}/poll/assessment
POST /v1/{project_code}/poll/summary
GET  /health
```

Responses are wrapped in `{"status": "OK" | "ERROR", "data": ...}` — the
same envelope the Kotlin backend used, so the existing `calc-web` frontend
doesn't need a rewrite to switch to this API (only `REACT_APP_API_BASE`
changes / `project_code` is added to the path).

Locale is still the `locale` header (see `app/api/deps.py`), matching the
original service.

An optional `secondary-locale` header asks for a second language in the same
response: every localized field gets a `*Secondary` twin (`contentSecondary`,
`riskTextSecondary`, ...). radar-women uses it to print the Kyrgyz mirror
under every question and to let the reader flip the prose blocks between
languages without reloading. The mirror never falls back to the project
default — a missing translation comes back empty rather than repeating the
primary text — and clients that don't send the header (calc-web) get those
fields as null.

## Multi-select questions

A question with multiple selectable answers (used in the "Женщины Ферганы"
questionnaire) needed no model or scoring changes: the client just sends
several `AnswerSelect` entries with the same `question_id` —
`compute_indicators` averages them together with every other answer of the
step, exactly like any other weight.

## Project layout

```
app/
  core/        — settings (pydantic-settings), async engine/session
  models/      — SQLAlchemy ORM
  schemas/     — Pydantic request/response models
  services/    — business logic (poll/indicator/summary/i18n)
  api/         — FastAPI routers and dependencies (get_project, get_locale, get_db)
  main.py      — app assembly, CORS, global error handler
alembic/       — migrations
tests/         — pytest suite (see Testing below)
scripts/
  seed_demo.py               — inserts a minimal demo project for manual API checks
  etl_zhashyl_climate.py     — one-off import of the legacy "Жашыл климат" data
  seed_fergana_women.py      — (re-)loads "Женщины Ферганы" from scripts/data/fergana_women.json
  copy_regions_to_fergana.py — copies the Region/Area tree into fergana-women (see below)
  data/fergana_women.json    — the questionnaire content itself, ru+ky
docs/
  fergana-women-content-spec.md — mapping notes from the source PDF/docx to the JSON above
```

## Build

```
deploy/
  docker/Dockerfile   — multi-stage: uv sync in the builder stage, minimal
                        runtime image (python:3.13-slim + .venv), port 8000
  config/dev.env       — environment variables for the dev environment (RADAR_*)
scripts/
  build-image.sh        — docker build with the project root as context
```

```bash
./scripts/build-image.sh                 # radar-api:dev
./scripts/build-image.sh radar-api:v1.2  # custom tag
```

The image doesn't drag anything extra into the build: the Dockerfile only
copies `pyproject.toml`/`uv.lock`/`app`/`alembic`/`alembic.ini`, so a heavy
local `.venv` or caches sitting in the build context don't matter (BuildKit
doesn't upload files that are never referenced).

There's no CI yet (see "Not done yet"), so deployment is manual: build the
image locally, transfer it to the server's Docker daemon, then recreate the
`radar-api` service in the shared `docker-compose.yml` at
`/opt/docker/compose/biom_app/` (which also runs `postgres`, `calc-web`,
`radar-women` and a couple of unrelated apps behind one host nginx +
Certbot per domain):

```bash
./scripts/build-image.sh kg.biom/radar-api:dev
docker save kg.biom/radar-api:dev | ssh aws.biom.node1 "docker load"
ssh aws.biom.node1 "cd /opt/docker/compose/biom_app && \
  docker compose up -d --force-recreate radar-api && \
  docker compose restart proxy"   # the proxy container caches the old IP otherwise
```

Migrations run the same way, against the tunnelled prod DB (see "Running
locally" for the tunnel):

```bash
RADAR_DATABASE_URL="postgresql+asyncpg://<user>:<pass>@localhost:5441/radar" \
  uv run alembic upgrade head
```

## Running locally

Locally this uses a dedicated Postgres 17 (same major version as
production) in its own container — not the shared `postgresql` container
other projects on this machine use:

```bash
docker run -d --name radar-postgres \
  -e POSTGRES_USER=radar -e POSTGRES_PASSWORD=radar -e POSTGRES_DB=radar \
  -p 5433:5432 -v radar_pg17_data:/var/lib/postgresql/data \
  postgres:17-alpine

cp .env.example .env   # already points at localhost:5433
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Quick manual check without a real radar's data:

```bash
PYTHONPATH=. uv run python scripts/seed_demo.py
curl -H "locale: ru" http://127.0.0.1:8000/v1/demo/poll/steps
```

## Testing

The test suite exercises the actual Postgres engine (JSONB, native enums)
rather than mocking the database, so it needs a real — disposable — test
database next to the dev one:

```bash
docker exec radar-postgres psql -U radar -d postgres -c "CREATE DATABASE radar_test OWNER radar;"
uv run pytest
```

`tests/conftest.py` creates the schema once per test session and wraps each
test in a transaction that's rolled back afterwards, so tests stay isolated
without recreating tables every time. Coverage focuses on the logic that
actually needs to be pinned down across a rewrite:

- `test_i18n.py` — locale fallback chain (requested → project default → any
  available translation → `None`).
- `test_indicator_service.py` — the scoring formula itself: flat average
  across a step regardless of which question an answer belongs to
  (multi-select), rounding to one decimal place, indicator/step isolation,
  inclusive risk-zone boundaries, the no-thresholds-configured case
  (always "low", matching "Жашыл климат" today), and locale fallback on
  risk text.
- `test_poll_service.py` — localization, region/area nesting and ordering,
  per-answer recommendation and `is_multi_select` passthrough.
- `test_api_poll.py` — the actual HTTP contract end-to-end (envelope shape,
  404 for an unknown project, missing-locale-header default) via FastAPI's
  ASGI transport with the DB dependency overridden to the test session.

## Done: "Жашыл климат" ETL

`scripts/etl_zhashyl_climate.py` imports that radar from the legacy Kotlin
`calc` schema into the new model. The source is **not production directly**
but a local, disposable copy of it:

```bash
# on a machine with an SSH tunnel to prod (LocalForward :5441 -> prod:5432)
docker run --rm -e PGPASSWORD=*** postgres:17-alpine \
  pg_dump -h host.docker.internal -p 5441 -U bmuser -d biom -n calc \
  --no-owner --no-privileges > calc_schema_dump.sql

# restore into a disposable local db and run the ETL against it
createdb calc_zhashyl_export && psql -d calc_zhashyl_export -f calc_schema_dump.sql
PYTHONPATH=. uv run python scripts/etl_zhashyl_climate.py
```

Production was never modified — just one read-only `pg_dump`, scoped to the
`calc` schema. Every later run/debugging pass worked against the local copy.

What the transform accounts for:

- Primary keys are preserved 1:1 (`step`, `region`, `area`, `indicator`,
  `question`, `answer`) — no FK remapping needed, easy traceability back to
  the source ids; each table's sequence is reset to `MAX(id)` after load.
- `hstore` translations (`*_lang`) are merged with the base `ru` text into a
  single `JSONB {"ru": ..., "ky": ...}` via `merge_translations()`.
- `next_step_id` in the source schema is a separate table
  (`step_cascade_next(step_id, next_id)`), not a column. Ported as a
  two-pass load: insert every `step` with `next_step_id=NULL` first
  (otherwise the self-referential FK fails on a not-yet-inserted next
  step), then `UPDATE` from the `next_map`.
- SQLAlchemy has no insertion-order dependency information without
  `relationship()` between models — explicit `db.flush()` calls separate
  the table blocks (step → region → area → indicator/question → answer).
- `answer.recommendation` and indicator risk-zone thresholds/texts didn't
  exist in the source schema, so they stay `NULL`. Nothing breaks: `risk_text`
  simply isn't returned (as before, `calc-web` never displayed it), and
  `risk_zone` resolves to "low" by default (no thresholds, no signal).
- Verified end-to-end: `steps`/`regions`/`assessment` in both ru and ky,
  and `POST /summary` with real (not demo) weights — an indicator with
  max-weight answers correctly computes `value=3.0`, untouched ones `0.0`.

Idempotent: the script drops `project(code='zhashyl-climate')` wholesale
(`ON DELETE CASCADE` clears every child row) and reloads it — safe to
re-run any number of times.

## Done: "Женщины Ферганы" seed

Unlike "Жашыл климат", there's no legacy database to ETL from — the
questionnaire only ever existed as a PDF/docx, hand-transcribed into
`scripts/data/fergana_women.json` (mapping decisions are in
`docs/fergana-women-content-spec.md`). Every localizable field in that JSON
is `{"ru": "...", "ky": "..."}` (or `null`), loaded as-is (`seed_fergana_women.py`'s
`loc()` is a pure passthrough — the JSON already has the shape the DB wants).

```bash
PYTHONPATH=. uv run python scripts/seed_fergana_women.py
PYTHONPATH=. uv run python scripts/copy_regions_to_fergana.py
```

**Both scripts must be run together, in that order, every time** —
`seed_fergana_women.py` replaces `project(code='fergana-women')` wholesale
(`delete(Project)...`, same idempotent pattern as the zhashyl-climate ETL),
and the cascade wipes any Region/Area rows and the REGION step, since those
were added by the *other* script. `copy_regions_to_fergana.py` copies the
Region/Area tree from `zhashyl-climate` verbatim under new PKs (fergana-women
intentionally reuses the exact same regions — same physical breakdown of
Kyrgyzstan, confirmed with the project owner) and inserts a REGION step at
the front of the step chain. Content currently loaded: 9 indicators, 100
questions, 390 answers, plus the region step and the radar step — 11 steps
total.

The questionnaire also has a few multi-select questions and per-answer
`recommendation` texts (see "Multi-select questions" above) — both worked
without any schema changes, since the original model already carried a
`weight` and an optional `recommendation` per answer.

## CI/CD

`.github/workflows/` holds three workflows, all running on `ubuntu-24.04-arm`
because production is aarch64 — building on the same architecture means CI
tests what actually ships, and no QEMU is involved.

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | push to `main`, any PR | ruff, mypy --strict, pytest against a real Postgres 17 service |
| `deploy.yml` | manual (`workflow_dispatch`) | builds `linux/arm64`, pushes `ghcr.io/<owner>/radar-api:dev` + `:sha-<short>`, then over SSH: `docker compose pull` / `up -d` / `restart proxy` / `image prune`, then a health check |
| `seed.yml` | manual, needs `confirm: seed` | re-runs `seed_fergana_women.py` + `copy_regions_to_fergana.py` on the server against the chosen ref |

Deployment is deliberately manual rather than push-to-deploy: an API release
often has to be paired with a content re-seed, and the two are separate
workflows on purpose.

Repository secrets used by both deploying workflows: `DEPLOY_HOST`,
`DEPLOY_USER`, `DEPLOY_SSH_KEY` (a dedicated ed25519 key, not a personal one).
Rolling back is `docker compose up -d` on the server with the image pinned to
an older `:sha-…` tag — every deploy publishes one.

## Not done yet

- An admin UI, or at least CLI scripts, for content CRUD (right now the
  only way to populate or fix data is to write SQL/Python scripts, and
  reseeding "Женщины Ферганы" requires remembering to re-run
  `copy_regions_to_fergana.py` afterwards — see above).
