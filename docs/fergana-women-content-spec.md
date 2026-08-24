# Content spec: "Женщины Ферганы" radar

Decisions made while mapping `radar_questionary_womens_fergana.pdf` (37 pages, "ВОПРОСНИК
ДЛЯ ПРОВЕДЕНИЯ САМООЦЕНКИ МЕСТНЫХ СООБЩЕСТ ПО ОЦЕНКЕ УЯЗВИМОСТИ К ИЗМЕНЕНИЮ КЛИМАТА") onto
the radar-api schema, agreed with the user. This is the reference for whoever (human or
Claude) writes the actual seeding script — it does not itself transcribe all 100 questions.

## Project / structure

- `project.code = "fergana-women"`, name "Женщины Ферганы" (proposed default, never
  explicitly contested — treat as adopted unless corrected).
- 9 `step` rows of type `ASSESSMENT` (one per "Показатель"), in document order, **no**
  `REGION` step — this project has no district/area picker, unlike "Жашыл климат".
- 1 final `step` of type `RADAR`.
- 1 `indicator` per ASSESSMENT step (1:1, same pattern as zhashyl-climate).

## Question count: 100, not 105

The intro list in the PDF claims 105 questions total (sum of the "N вопросов" per
indicator), but the actual question rows present in the tables total **100**. Three
indicators have gaps in their own numbering (not a PDF-extraction artifact — verified by
re-reading row by row):

| Показатель | Заявлено | Факт | Отсутствуют № |
|---|---|---|---|
| 5. Среда населённых пунктов | 17 | 14 | 2, 4, 5 |
| 7. Гендер и климатическая устойчивость | 9 | 8 | 8 |
| 9. Механизмы миростроительства | 8 | 7 | 5 |

**Decision**: seed exactly the 100 questions that exist, using each question's original PDF
number as `question.ord` (gaps in `ord` are fine, the schema doesn't require contiguity).
Do not fabricate the missing ones. Can be added later if the source is updated.

## Answer weight derivation

- If an answer cell already contains a literal digit (0/1/2/3), that digit **is** the
  weight — use it directly.
- If an answer cell only has descriptive text (no digit shown), the weight is its **position**
  left→right: 1st column = 0, 2nd = 1, 3rd = 2, 4th = 3. Checked across the whole document:
  the grid is always ascending left→right with no exceptions — the parenthetical legend text
  next to the question sometimes *lists* the meanings in a different (often descending,
  "best first") order, but the grid columns themselves never are.
- Some questions have fewer than 4 real options (e.g. Показатель 5, №7 "Наличие очагов особо
  опасных инфекций" has only two: weight 0 = "есть", weight 3 = "нет" — the two middle grid
  cells are blank in the source). This is expected/normal, not an error — only create
  `Answer` rows for the options that actually have content.

## Risk-zone thresholds (uniform across all 9 indicators)

`indicator.high_risk_max = 1`, `indicator.medium_risk_max = 2` for every indicator (i.e.
value ≤ 1 → high risk, ≤ 2 → medium, > 2 → low). Not a guess — derived empirically from the
grey/blue/white answer-cell background shading used throughout the document (grey = weight
0–1, blue = weight 2, white/no fill = weight 3), confirmed consistent across a dozen+ spot
checks in different indicators.

## Text content: three kinds, three different schema slots

The PDF has three distinct kinds of narrative text per indicator, in different colors, that
map to three different places:

1. **Blue text, before the question rows** ("Показатель N. ... | Рекомендации" header, then
   this paragraph, then Q1). This is a description of the indicator itself.
   → new field **`step.intro`** (JSONB, nullable — does not exist yet, needs a migration).
   Rendered right under the step name (`<h1>`), visible while the user is answering that
   step's questions — **not** gated by anything.

2. **Blue text, after the last question row**, always shown once the user finishes that
   step's questions, **regardless of which answers were picked**.
   → existing **`step.descr`** field — already used exactly this way by "Жашыл климат"
   (rendered in `Resume.tsx` after a step is completed, before the "Далее" button).

3. **Black text, after the last question row, structured as "1. Высокая зона риска / 2.
   Средний уровень риска / 3. Низкий уровень риска"** with bullet lists under each. This
   **is** gated — which one is shown depends on the indicator's *computed* score (the same
   `high_risk_max`/`medium_risk_max` thresholds above).
   → existing **`indicator.high_risk_text` / `medium_risk_text` / `low_risk_text`** fields.

**Not content** — explicitly excluded from seeding, these are notes for whoever maintains
the source spreadsheet, not end-user text:
- The repeated legend *"Ответы с серой заливкой: необходимо предпринять меры… голубой…
  белой…"* (appears after Показатели 7, 8, 9) — explains the *spreadsheet's* cell shading,
  meaningless in our UI which has no colored cells.
- The one-line note *"Рекомендации формируются из последней колонки исходя из баллов"*
  between Показатель 6 and 7 — an authoring transition note, not indicator content.

## Per-answer recommendations

Last column ("Рекомендации") of each question row → `answer.recommendation`. The text
usually covers a *range* of answers (e.g. "0-2. [text]") — attach the **same** text to every
answer in that range, leave the safest answer (usually weight 3, sometimes the top of a
narrower range) with `recommendation = null`. Where the column is blank for a question, all
its answers get `recommendation = null`.

**Display timing** (frontend note, not a schema decision): these are **not** shown live on
answer-click. They're collected and shown together, once, on the same completion/"Resume"
screen as `step.descr` — after the user finishes all of that step's questions.

## Per-indicator content matrix (final, confirmed)

| # | Показатель | Вопросов | `step.intro` | `step.descr` | `high_risk_text` | `medium_risk_text` | `low_risk_text` |
|---|---|---|---|---|---|---|---|
| 1 | Окружающая среда | 10 | есть | есть | есть | **нет в источнике → null** | есть |
| 2 | Сельское хозяйство | 15 | есть | есть | есть | есть | есть |
| 3 | Ирригационные ресурсы и инфраструктура | 13 | есть | есть | есть | есть | есть |
| 4 | Вода, санитария, гигиена | 13 | **null — предоставят позже** | есть | есть | есть | есть |
| 5 | Среда населённых пунктов | 14 | есть | есть | есть | есть | есть |
| 6 | Потенциал местного сообщества | 11 | нет | нет | =текст ниже | =текст ниже | =текст ниже |
| 7 | Гендер и климатическая устойчивость | 8 | нет | есть | нет | нет | нет |
| 8 | Климатические риски и социальная напряжённость | 9 | есть | нет | нет | нет | нет |
| 9 | Механизмы миростроительства | 7 | нет | нет | нет | нет | нет |

**Показатель 6 special case**: the source has one continuous black paragraph ("Уязвимость
местных сообществ в Кыргызстане во многом определяется их высокой зависимостью от
аграрного сектора…"), not split into three risk-zone-labeled blocks like 1–5 have.
**Decision**: duplicate that single paragraph into all three of `high_risk_text` /
`medium_risk_text` / `low_risk_text` — the score-gating mechanism still runs, it just shows
the same text regardless of which zone the score lands in.

## Multi-select question

Показатель 5, question 13: *"Какие природные ЧС наиболее часто происходят в вашем
сообществе? Можно выбрать несколько вариантов."* — `question.is_multi_select = true`, four
answers:

| Ответ | Вес |
|---|---|
| Засухи и длительная жара | 0 |
| Сильные ливни и паводки, снегопады, сели | 0 |
| Сильный ветер/бури | 0 |
| За последние годы серьёзных ЧС не было | 3 |

No special aggregation logic needed — the existing flat-average-of-selected-weights
mechanism (`compute_indicators`) already produces the desired result on its own: picking any
combination of the first three (1, 2, or all 3) averages to 0 ("высокий риск"); picking only
the fourth gives 3. (An earlier plan to add a `question.include_in_score` exclusion flag was
dropped — turned out to be unnecessary once the weights were set this way.)

## Implementation checklist (not done yet)

- [ ] Add `step.intro` (JSONB, nullable) to the model + Alembic migration.
- [ ] Write `scripts/etl_fergana_women.py` (or similar) — source is the PDF itself (manual
      transcription), not a live database like the zhashyl-climate ETL. ~100 questions,
      ~300+ answers, 9 indicators with thresholds/risk texts as above.
- [ ] Показатель 4's `step.intro` — currently unknown, to be supplied by the user later; seed
      as `null` for now, don't block the rest of the import on it.
- [ ] Decide the frontend question separately (new app vs. extending `calc-web`) — not yet
      discussed.
