# radar-api

Бэкенд для семейства радар-калькуляторов (самооценка сообществ по показателям
устойчивости/уязвимости). Заменяет прежний Kotlin/Spring-сервис `calc` и
рассчитан на то, что с одним бэкендом будет работать несколько независимых
фронтендов-опросников (`calc-web` — «Жашыл климат», `fergana-women` и другие
в будущем).

## Стек

FastAPI + SQLAlchemy 2.0 (async) + asyncpg + Alembic + Pydantic v2.
Тулинг: `uv` (зависимости/venv), `ruff` (lint), `mypy --strict` (типы).

## Доменная модель

Один и тот же generic-набор сущностей обслуживает любой радар-опросник:

```
project        — верхнеуровневый проект/калькулятор (code, name, default_locale)
step           — шаг опроса: REGION | ASSESSMENT | RADAR, привязан к project
region / area  — гео-справочник (нужен не всем проектам; шаг REGION просто не создаётся)
question       — вопрос, привязан к step
answer         — вариант ответа, имеет вес (weight) и опциональный текст recommendation
indicator      — луч радара: 1:1 с ASSESSMENT-шагом (indicator.step_id)
```

Переводимые поля (`name`, `content`, `descr`, `recommendation`, `impact`,
risk-тексты) хранятся как `JSONB` вида `{"ru": "...", "ky": "..."}` и
резолвятся в сервисном слое (`app/services/i18n.py`) с фолбэком на
`project.default_locale`. Это сознательный отход от исходной Kotlin-схемы,
где переводы жили в отдельных `*_lang`-таблицах с `hstore` и резолвились
Postgres-функциями (`calc.step(_lang)` и т.п.) — тот подход работал, но
переносить хранимые SQL-функции в новый стек не было смысла: JSONB +
Python-фолбэк проще отлаживать и тестировать вне БД.

### Расчёт индикатора

Значение индикатора — плоское среднее `weight` всех выбранных ответов, у
которых `AnswerSelect.step_id == indicator.step_id` (без промежуточного
усреднения по вопросам). Это и есть та точная формула, что была в исходном
`IndicatorService.calcValue` — при переносе не менялась.

Зона риска — по настраиваемым порогам **на каждый индикатор**
(`indicator.high_risk_max`, `indicator.medium_risk_max`), а не по глобальной
константе: `value <= high_risk_max` → high, иначе `<= medium_risk_max` →
medium, иначе low. Это позволяет разным проектам иметь разную шкалу (не
только 0–3), не трогая код.

## Мультитенантность и API

Проект определяется сегментом пути: `/v1/{project_code}/poll/...`. Это
намеренно path-параметр, а не заголовок (как `locale`) — это адрес ресурса,
а не презентационная настройка: так проще фильтровать по origin в CORS,
логировать и кэшировать по проекту.

```
GET  /v1/{project_code}/poll/steps
GET  /v1/{project_code}/poll/regions
GET  /v1/{project_code}/poll/assessment
POST /v1/{project_code}/poll/summary
GET  /health
```

Ответы завёрнуты в `{"status": "OK" | "ERROR", "data": ...}` — тот же
конверт, что отдавал Kotlin-бэкенд, чтобы существующий `calc-web` не
пришлось переписывать при переключении на новый API (меняется только
`REACT_APP_API_BASE`/добавляется `project_code` в путь).

Локаль — по-прежнему заголовок `locale` (см. `app/api/deps.py`), как в
исходном сервисе.

## Мультиселект

Вопрос с несколькими вариантами ответа (встречается в опроснике «Женщины
Ферганы») не потребовал изменений в модели/расчёте: клиент просто
присылает несколько записей `AnswerSelect` с одинаковым `question_id` —
`compute_indicators` усредняет их вместе со всеми остальными ответами шага,
как и любые другие веса.

## Структура проекта

```
app/
  core/        — настройки (pydantic-settings), async engine/session
  models/      — SQLAlchemy ORM
  schemas/     — Pydantic request/response
  services/    — бизнес-логика (poll/indicator/summary/i18n)
  api/         — FastAPI-роутеры и зависимости (get_project, get_locale, get_db)
  main.py      — сборка приложения, CORS, глобальный обработчик ошибок
alembic/       — миграции
scripts/seed_demo.py — вставка минимального демо-проекта для ручной проверки API
```

## Запуск локально

Локально используется отдельный Postgres 17 (та же мажорная версия, что и
на проде) в собственном контейнере — не общий `postgresql`-контейнер,
которым пользуются другие проекты:

```bash
docker run -d --name radar-postgres \
  -e POSTGRES_USER=radar -e POSTGRES_PASSWORD=radar -e POSTGRES_DB=radar \
  -p 5433:5432 -v radar_pg17_data:/var/lib/postgresql/data \
  postgres:17-alpine

cp .env.example .env   # уже настроен на localhost:5433
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Проверка без реальных вопросников:

```bash
PYTHONPATH=. uv run python scripts/seed_demo.py
curl -H "locale: ru" http://127.0.0.1:8000/v1/demo/poll/steps
```

## ETL «Жашыл климат» (сделано)

`scripts/etl_zhashyl_climate.py` переносит проект из legacy Kotlin-схемы
`calc` в новую модель. Источник — **не прод напрямую**, а его локальная
разовая копия:

```bash
# на машине с SSH-туннелем к проду (LocalForward :5441 -> prod:5432)
docker run --rm -e PGPASSWORD=*** postgres:17-alpine \
  pg_dump -h host.docker.internal -p 5441 -U bmuser -d biom -n calc \
  --no-owner --no-privileges > calc_schema_dump.sql

# восстановить в одноразовую локальную БД и запустить ETL против неё
createdb calc_zhashyl_export && psql -d calc_zhashyl_export -f calc_schema_dump.sql
PYTHONPATH=. uv run python scripts/etl_zhashyl_climate.py
```

Прод не модифицировался — только один read-only `pg_dump`, ограниченный
схемой `calc`. Все дальнейшие прогоны/отладка ETL шли уже против локальной
копии.

Что учтено при переносе:

- Первичные ключи сохранены 1:1 (`step`, `region`, `area`, `indicator`,
  `question`, `answer`) — FK не нужно перематывать, easy traceability к
  исходным id; после загрузки sequence каждой таблицы выставляется на
  `MAX(id)`.
- `hstore`-переводы (`*_lang`) склеены с базовым `ru`-текстом в единый
  `JSONB {"ru": ..., "ky": ...}` через `merge_translations()`.
- `next_step_id` в исходной схеме — отдельная таблица
  `step_cascade_next(step_id, next_id)`, а не колонка. Перенесено в
  двухпроходную загрузку: сначала все `step` с `next_step_id=NULL`
  (иначе self-referential FK падает на ещё не вставленной следующей
  записи), затем `UPDATE` по карте `next_map`.
- Без `relationship()` между ORM-моделями SQLAlchemy не знает порядок
  вставки по зависимостям — между блоками таблиц расставлены явные
  `db.flush()` (step → region → area → indicator/question → answer).
- Полей `answer.recommendation` и risk-zone порогов/текстов индикатора в
  исходной схеме не было — остаются `NULL`. Это ничего не ломает: `risk_text`
  просто не возвращается (как и раньше `calc-web` его не показывал), а
  `risk_zone` резолвится в "low" по дефолту (нет порогов — нет сигнала).
- Проверено end-to-end: подняты `steps`/`regions`/`assessment` в ru и ky,
  прогнан `POST /summary` с реальными весами (не демо) — индикатор с
  ответами max-веса корректно даёт `value=3.0`, остальные (без ответов)
  — `0.0`.

Идемпотентно: скрипт грохает `project(code='zhashyl-climate')` целиком
(`ON DELETE CASCADE` подчистит все дочерние строки) и заливает заново —
можно перезапускать сколько угодно.

## Что дальше (не сделано в этом скелете)

- **Данные проекта «Женщины Ферганы»**: наполнение по опроснику (9
  показателей, ~105 вопросов, тексты рекомендаций и risk-zone нарративы)
  — кандидат на отдельный сидинг-скрипт по образцу `etl_zhashyl_climate.py`/
  `seed_demo.py` (данных в исходной БД для него нет — вопросник только в PDF).
- Тесты (`pytest-asyncio` уже в dev-зависимостях, тестов пока нет).
- Docker-образ/деплой.
- Админка или хотя бы CLI/скрипты для CRUD над контентом (сейчас
  единственный способ наполнить/поправить БД — писать SQL/Python-скрипты).
