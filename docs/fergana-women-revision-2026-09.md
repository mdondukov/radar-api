# «Женщины Ферганы» - update specification (September 2026)

Basis: expert comments (Kirilenko Anna, `radar_women.docx`, 3 September 2026,
tracked changes). This document turns those comments into an exact list of
changes to content, API and UI.

Scope: project `fergana-women` (frontend `radar-women`, backend `radar_api`).
Project `zhashyl-climate` / `calc-web` is not affected content-wise, except for one
shared API bug (§5.1).

---

## 0. Scope

| Block | Questions | In scope |
|---|---|---|
| Edits from the expert's document | 29 + 1 deletion | yes |
| «Сельское хозяйство» (Agriculture): moving the author's explanations onto the buttons | 15 | yes |
| Other indicators with numeric scales | 23 | **no** |

Decision: we change strictly what the expert pointed out. «Сельское хозяйство» is in scope
because it is her separate comment («если ставишь все 3, всё равно средний балл
два — исправить», "if you give all 3s, the average is still two - fix it"), and it cannot be fixed any other way (§2).

Out of scope are questions in other indicators where the scale is labeled with digits and
the explanation lives in the question text. The questionnaire will temporarily stay mixed: some
questions with word buttons, some with digits. This is a deliberate price for
not second-guessing the expert.

---

## 1. Content: edits from the expert's document

Entry format: `option text` → weight. Option order is kept as it is now.
Explanations that the expert added to the question text **are moved onto the buttons and
removed from the question text**, otherwise they would be duplicated on screen.

Numbering below is `ord` in the database. The expert's document uses its own numbering in places
(see §7); matching was done by question text.

### 1.1. Ирригационные ресурсы и инфраструктура (Irrigation resources and infrastructure)

**ord=1 · Как вы оцениваете общее состояние ирригационных каналов и сооружений в вашем районе?**
- RU: `плохо` 0 · `есть проблемы` 1 · `есть отдельные сложности, но в целом хорошо` 2 · `очень хорошо` 3
- KY: `начар` · `көйгөйлөр бар` · `айрым кыйынчылыктар бар, бирок жалпысынан жакшы` · `абдан жакшы`

**ord=2 · Насколько предсказуем график подачи воды?**
- RU: `не понятно, когда дают воду` 0 · `дают воду по устной договорённости` 1 · `есть график, но не всегда исполняется` 2 · `есть чёткий график, которого придерживаются` 3
- KY: `суу качан берилери түшүнүксүз` · `суу оозеки келишим боюнча берилет` · `график бар, бирок ар дайым аткарылбайт` · `так график бар жана ага карманышат`

**ord=3 · Доступность воды**
- RU: `воды остро не хватает` 0 · `вода есть, но хватает не всем` 1 · `в целом хватает, но бывают отдельные периоды` 2 · `воды хватает всем, проблем нет` 3
- KY: `суу өтө жетишпейт` · `суу бар, бирок баарына жетпейт` · `жалпысынан жетет, бирок айрым мезгилдер болот` · `суу баарына жетет, көйгөй жок`

**ord=5 · Оцените потери воды для полива в вашем сообществе**
- RU: `очень высокие` 0 · `высокие` 1 · `средние` 2 · `почти нет потерь` 3
- KY: `өтө жогору` · `жогору` · `орточо` · `жоготуулар дээрлик жок`

**ord=6 · rewording + scale**
- Question text RU: ~~Степень использования земляных каналов без бетонирования и лотков~~ → **Как часто используются земляные каналы без бетонирования и лотков**
- Question text KY: **Бетондолбогон жана науасыз жер каналдары канчалык көп колдонулат**
- RU: `все каналы без бетонирования` 0 · `только отдельные забетонированы` 1 · `больше половины забетонированы` 2 · `практически все забетонированы` 3
- KY: `бардык каналдар бетондолгон эмес` · `айрымдары гана бетондолгон` · `жарымынан көбү бетондолгон` · `дээрлик баары бетондолгон`

> Note on ord=6: the question asks about the use of earthen canals, while the scale
> describes the degree of concrete lining; this is how the expert wrote it. The word
> «забетонированы» was added to the last option (the expert has just «практически все»), otherwise
> the button reads as "almost all canals are earthen", i.e. the opposite. This is
> the only meaning completion in the whole §1 block; submit it for confirmation.

### 1.2. Потенциал местного сообщества (Local community capacity)

**ord=3 · Наличие зарегистрированных неправительственных организаций на местном уровне (кроме политических организаций)**
- RU: `нет` 0 · `одна организация` 1 · `две организации` 2 · `три и более` 3
- KY: `жок` · `бир уюм` · `эки уюм` · `үч жана андан көп`

**ord=4 · Наличие инициативных групп**
- RU: `нет` 0 · `одна инициативная группа` 1 · `две` 2 · `три и более` 3
- KY: `жок` · `бир демилгелүү топ` · `эки` · `үч жана андан көп`

**ord=5 · Наличие женских организаций**: scale as in ord=3
**ord=6 · Наличие молодёжных организаций**: scale as in ord=3

**ord=7 · Информированность населения по вопросам изменения климата, адаптации и митигации**
- Question text: remove the tail «Люди, прошедшие повышение квалификации, обучение, повышение потенциала по вопросам ИК (5 и больше человек: 1)», which the expert struck out. The first sentence remains.
- KY text accordingly: up to «...кабардар болуусу.»
- RU: `вообще не знают о проблеме` 0 · `информированы единицы` 1 · `есть отдельные группы, которые информированы` 2 · `большинство информировано` 3
- KY: `көйгөй жөнүндө такыр билишпейт` · `жалгыз-жарымы кабардар` · `кабардар болгон айрым топтор бар` · `көпчүлүгү кабардар`

**ord=8 · Сообщество регулярно получает информацию из государственных и других источников по вопросам уязвимости к изменению климата**: the scale is replaced entirely
- RU: `не знаю` 0 · `не получает` 0 · `получает иногда` 2 · `регулярно получает` 3
- KY: `билбейм` · `албайт` · `кээде алат` · `дайыма алат`

**ord=9 · Сообщество реализует инициативы по снижению уязвимости к изменению климата**: the scale is replaced entirely
- RU: `не знаю` 0 · `не реализует` 0 · `реализует иногда` 2 · `регулярно реализует` 3
- KY: `билбейм` · `ишке ашырбайт` · `кээде ишке ашырат` · `дайыма ишке ашырат`

> Weight of «не знаю» = 0, same as «не получает» / «не реализует»: agreed.
> Consequence: weight 1 is not used in these two questions, the scale becomes 0/0/2/3.
> Two options with the same weight are acceptable here: their texts differ, unlike
> the «Достаточность пастбищ» case (§2).

### 1.3. Гендер и климатическая устойчивость (Gender and climate resilience)

**ord=3 · rewording + scale**
- Question text RU: ~~Испытывают ли женщины и мужчины одинаковые возможности доступа к воде для домашних и хозяйственных нужд?~~ → **Есть ли у женщин и мужчин одинаковый доступ к воде для домашних и хозяйственных нужд?**
- Question text KY: **Аялдар менен эркектердин үй-тиричилик жана чарбалык муктаждыктар үчүн сууга бирдей жетүү мүмкүнчүлүгү барбы?**
- RU: `нет` 0 · `в основном нет` 1 · `в основном одинаковый` 2 · `есть равенство` 3
- KY: `жок` · `негизинен жок` · `негизинен бирдей` · `теңдик бар`

**ord=4 · Имеют ли женщины достаточный доступ к земле и возможность участвовать в принятии решений о её использовании?**
- RU: `нет` 0 · `в основном нет` 1 · `в основном да` 2 · `есть равенство` 3
- KY: `жок` · `негизинен жок` · `негизинен ооба` · `теңдик бар`

**ord=5 · Получают ли женщины своевременную информацию о засухах, селях, паводках, жаре и других климатических рисках?**: **delete the whole question** together with its answer options.

**ord=6 · Увеличивает ли нехватка воды или другие климатические проблемы неоплачиваемую домашнюю нагрузку женщин?**
- RU: `да и сильно` 0 · `в основном да` 1 · `частично` 2 · `нет` 3
- KY: `ооба, катуу` · `негизинен ооба` · `жарым-жартылай` · `жок`

**ord=7 · Имеют ли женщины доступ к финансированию, технологиям, знаниям и обучению для адаптации к изменению климата?**
- RU: `нет` 0 · `в единичных случаях` 1 · `в основном да` 2 · `да` 3
- KY: `жок` · `жалгыз-жарым учурларда` · `негизинен ооба` · `ооба`

**ord=9 · Участвуют ли женщины в планировании действий при стихийных бедствиях и ЧС?**: scale as in ord=7

### 1.4. Климатические риски и социальная напряжённость (Climate risks and social tension)

**ord=3 · Возникают ли споры из-за доступа к пастбищам или их деградации?**
**ord=4 · Усиливаются ли после засух, селей, паводков или других климатических событий разногласия между жителями?**
- RU: `да и часто` 0 · `довольно часто` 1 · `изредка` 2 · `нет` 3
- KY: `ооба, көп` · `кыйла көп` · `сейрек` · `жок`

**ord=5 · Считают ли жители распределение воды, земли и других природных ресурсов справедливым?**
**ord=6 · Насколько жители доверяют решениям местных органов власти по вопросам природных ресурсов и климатических проблем?**
- RU: `нет` 0 · `только иногда` 1 · `в основном да` 2 · `да` 3
- KY: `жок` · `кээде гана` · `негизинен ооба` · `ооба`

**ord=7 · Приводят ли климатические проблемы к росту напряжённости между различными группами населения?**
- RU: `да и сильно` 0 · `в основном да` 1 · `частично` 2 · `нет` 3
- KY: `ооба, катуу` · `негизинен ооба` · `жарым-жартылай` · `жок`

**ord=8 · Приводят ли ухудшение условий жизни и нехватка ресурсов к миграции членов семей?**
**ord=9 · Увеличивает ли миграция нагрузку на оставшихся членов семьи, особенно женщин?**
- RU: `да` 0 · `часто` 1 · `иногда` 2 · `нет` 3
- KY: `ооба` · `көп` · `кээде` · `жок`

### 1.5. Механизмы миростроительства (Peacebuilding mechanisms)

**ord=2 · Есть ли люди или структуры, к которым жители обращаются для посредничества при возникновении споров?**: the scale is replaced with YES/NO
- RU: `нет` 0 · `да` 3
- KY: `жок` · `ооба`

**ord=3 · Участвуют ли женщины в разрешении споров и медиации?**
- RU: `нет` 0 · `в единичных случаях` 1 · `в основном да` 2 · `да` 3
- KY: `жок` · `жалгыз-жарым учурларда` · `негизинен ооба` · `ооба`

**ord=4 · rewording + scale**
- Question text RU: ~~Есть ли практика проведения регулярных обсуждений проблем воды, природных ресурсов или климатических рисков?~~ → **Проводятся ли регулярные обсуждения проблем воды, природных ресурсов или климатических рисков в местном сообществе?**
- Question text KY: **Жергиликтүү коомчулукта суу, жаратылыш ресурстары же климаттык тобокелдиктер боюнча маселелер үзгүлтүксүз талкууланабы?**
- Scale as in ord=3

**ord=7 · Существуют ли совместные инициативы разных групп жителей по управлению водой, природными ресурсами или адаптации к климату?**
- RU: `нет` 0 · `в единичных случаях` 1 · `есть позитивные примеры` 2 · `да, это распространённая практика` 3
- KY: `жок` · `жалгыз-жарым учурларда` · `оң мисалдар бар` · `ооба, бул кеңири таралган практика`

**ord=8 · Способны ли местные власти, жители и организации совместно реагировать на климатические проблемы?**: the scale is replaced with YES/NO (as ord=2)

> YES/NO get weights 0 and 3, following the questions of this type already in the
> questionnaire (Ирригация ord=9, ord=10). Consequence: in an indicator of 7 questions, two give
> only extreme values and noticeably jerk the average score. With thresholds
> `high_risk_max=1`, `medium_risk_max=2` this can flip the indicator between
> risk zones; take this into account during verification.

---

## 2. «Сельское хозяйство»: why the average score is 2 with "all 3s"

**Diagnosis.** The indicator has 15 questions. In five of them (`ord` 6, 10, 11, 12, 13) the scale
is inverted: the button labeled «3» has weight 0, because "we often suffer from
heat" is bad. The calculation is correct, but the person sees only digits:
10 × 3 + 5 × 0 = 30 / 15 = **exactly 2.0**, which is what the expert observed.

**Fix.** Move the author's explanations from the question text onto the buttons. Then «3»
stops existing as a concept, and with it the illusion "I picked the
maximum everywhere". No option's weight changes, only the labels change.
The explanations already exist in both languages (in the ky question text, in the same parentheses), so
no translation is needed.

**Formally:** for each question, take the `N — text` pair from the parentheses, assign the text
to the option labeled `N`, and remove the parentheses from the question text. Do not touch
option weights.

| ord | Buttons (RU, in current order) | Weights |
|---|---|---|
| 2 | отсутствие деградации · минимальная · существенная · сильная деградация | 0/1/2/3 |
| 3 | низкая · отвечает требованиям · больше положенного · очень большая нагрузка | 0/1/2/3 |
| 4 | не бывает · единичные случаи · довольно часто · часто | 0/1/2/3 |
| 5 | нет · есть, но низкого качества · есть, но нужно дорабатывать · есть хорошего качества | 0/1/2/3 |
| 6 | не бывает · единичные случаи · довольно часто · часто | 3/2/1/0 |
| 7 | критически недостаточно · недостаточно · есть проблемы, но в целом достаточно · достаточно полностью | 0/1/2/3 |
| 8 | не выращиваются · есть единичные домохозяйства · выращиваются · входят в число основных культур | 0/1/2/3 |
| 9 | никогда · редко · часто · очень часто | 0/1/2/3 |
| 10 | никогда · редко · часто · очень часто | 3/2/1/0 |
| 11 | никогда · редко · часто · очень часто | 3/2/1/0 |
| 12 | не привела · есть отдельные территории · это проблема для сообщества · серьёзная проблема | 3/2/1/0 |
| 13 | никогда · редко · часто · очень часто | 3/2/1/0 |
| 14 | нет примеров · одна теплица · есть несколько · распространённая практика | 0/1/2/3 |
| 15 | нет · один · несколько · распространённая практика | 0/1/2/3 |

Kyrgyz labels are taken from the ky text of the same questions, pairwise.

**ord=1 · Достаточность пастбищ** is a special case: the expert's explanation is
«0-1 критически недостаточно», i.e. 0 and 1 are described by the same wording.
Decision: **three buttons instead of four**.
- RU: `критически недостаточно` 0 · `достаточно, но есть проблемы` 2 · `достаточно` 3
- KY: `өтө жетишсиз` · `жетиштүү, бирок көйгөйлөр бар` · `жетиштүү`

The calculation does not suffer from this: the option with weight 1 duplicated the zero one in meaning.
Side effect: for those who previously chose «1», the indicator score will be
0.07 lower (1/15 of a one-point difference).

---

## 3. Kyrgyz translations

The expert sent edits **in Russian only**. The translations in §1 were done by me, based
on terminology already used in this questionnaire (`жок`, `ооба`, `жарым-жартылай`,
`сейрек`, `дайыма`, `негизинен`, `кеңири таралган практика` etc., 75 existing
answer option pairs).

**They need proofreading by a native speaker.** Check separately:
- `билбейм` («не знаю»): the questionnaire had no such option before;
- `жалгыз-жарым учурларда` («в единичных случаях»): built on the pattern of
  `үй чарбалардын жалгыз-жарымы бар`;
- the reworded texts of three questions (Ирригация ord=6, Гендер ord=3,
  Миростроительство ord=4): these are new sentences, not edits of existing ones.

The §2 translations do not need proofreading: they were already written by the expert group and sit in the question
texts; we only move them.

---

## 4. UI changes (`radar-women`)

### 4.1. Hint about an incomplete indicator
Currently the «Далее» button is simply disabled, with no explanation (`Questions.tsx`,
`buttons/ResumeButton.tsx`). Add next to it the text «Чтобы перейти в другую секцию,
ответьте на все вопросы» (ru + ky in `i18n/messages-*.json`).

### 4.2. Free navigation between indicators
`Navigation.tsx:47-63` allows going to a step only if it is already completed **and** the current one is also
completed. Allow going to any ASSESSMENT step in any order.

Restrictions that remain:
- **RADAR** opens only when all nine indicators are filled in. Otherwise
  unfilled axes go into the calculation as zeros (`indicator_service.py:63`) and the person
  sees an unreliable chart.
- **REGION** stays the first mandatory step: `Radar.tsx:186` dereferences
  `regionStore.selectRegion` without a null check; without a region the screen crashes.

Related:
- `getColor()` in `Navigation.tsx` gets a fourth state, "available but not
  filled in" (currently: active / completed / unavailable).
- Fix `StepStore.setIncompleteStep`: `filter(id => id === stepId)` leaves only this step
  in the list instead of removing it. The method is not called now,
  but with free navigation it is easy to start using it.
- Answers are not lost when switching steps: they are stored in the shared
  `QuestionStore._selectAnswers` keyed by `stepId`. No extra work
  needed, but it must be in the test plan.

> **Revised on 4 September 2026.** Free forward navigation is cancelled: in practice
> it produced a radar of empty indicators (jumping straight to the last indicator,
> answering, pressing «Далее» twice - and a radar with eight zero axes). Current rule:
> backward - free, including from a partially filled indicator; forward - only up to
> the furthest step already reached; radar - only when all nine
> indicators are answered, with a list of unfilled ones. The expert's repeated request for free
> order (October 2026) was rejected on these grounds, see
> `fergana-women-revision-2026-10.md`, §1.

### 4.3. Kyrgyz mirror of questions and answers
Under each question and each answer option, show the Kyrgyz text in a different
color (visually subordinate to the main one). Requires §5.2.

### 4.4. Language switch in the information and recommendation blocks
Two buttons «Русский / Кыргызча» in the `Resume.tsx` and `Radar.tsx` cards, acting
locally on `step.intro`, `step.descr`, `answer.recommendation`,
`indicator.riskText` and the «География» text (`area.descr`, `area.impact`), without changing the language
of the whole UI. Requires §5.1 and §5.2.

### 4.5. Final document in the selected language
«Скачать результат» is `window.print()` (`Radar.tsx:258`); the current DOM is printed.
After §4.4 it is enough to print the language selected in the cards; separate buttons
«Скачать рус / Скачать кырг» would require re-rendering the page before printing and are
not in this scope.

### 4.6. Minor items
- `Question.tsx:57`: `answer.content.toLowerCase()` will break abbreviations with word options
  («ЧС» → «чс»). Remove the case conversion; write option texts
  in the correct case from the start.
- Check wrapping of long button labels: a button used to hold one digit, now
  up to 40 characters. Affects `getButtonClass()` (desktop button row);
  the row will probably have to switch to line wrapping.

---

## 5. API changes (`radar_api`)

### 5.1. Bug: `POST /summary` ignores the language
`fetchIndicators()` (`radar-women/src/http/api.ts:32`) does not send the `locale` header,
although the endpoint reads it (`app/api/deps.py:get_locale`). The server falls back to
`settings.default_locale = "ru"`, so **on the Kyrgyz version of the site the risk zone
texts and recommendations are currently always in Russian**. Fixed by sending the header.

The same bug is in `calc-web`; check and fix it there too.

### 5.2. Returning two languages at once
For §4.3 and §4.4 the client needs both locales at the same time. The proposed solution
is additive, so as not to break `calc-web`:

- optional request header `secondary-locale: ky`;
- paired fields appear in the response: `contentSecondary`, `nameSecondary`,
  `introSecondary`, `descrSecondary`, `recommendationSecondary`, `riskTextSecondary`,
  `impactSecondary` (camelCase on the wire, per the common contract, see
  `app/schemas/common.py`);
- without the header these fields come as `null`, so `calc-web` keeps
  getting exactly one language and simply ignores the extra keys;
- the mirror does **not** fall back to the default language: if there is no translation, the field
  is empty. Otherwise a "Kyrgyz" line would silently show Russian text.

Affects `app/api/deps.py`, `app/schemas/{question,step,summary,region}.py`,
`app/services/{poll_service,summary_service,indicator_service}.py`, `app/services/i18n.py`.

The alternative (two requests from the client and merging by id) was rejected: it doubles network
requests and does not help `POST /summary`, where there is nothing to merge.

---

## 6. Order of application

1. **Data.** Apply the §1 and §2 edits to `scripts/data/fergana_women.json`.
   Re-seed: `PYTHONPATH=. uv run python scripts/seed_fergana_women.py`.
   Re-seeding is safe: user runs are not stored on the server at all
   (answers come in `POST /summary` from the client and are not written anywhere), so
   `replace_project` destroys nothing. Regions are restored after re-seeding by
   the `scripts/copy_regions_to_fergana.py` script, which also inserts the REGION step at the
   start of the chain.
2. **API.** §5.1, then §5.2 + tests (`pytest`, real `radar_test` on
   `radar-postgres`).
3. **Frontend.** §4.1–4.6.
4. **Deploy.** `scripts/build-image.sh`, `docker save/load` on `aws.biom.node1`,
   re-seed on the prod database, `docker image prune -f` afterwards (otherwise dangling layers pile up).
5. **Verification.** Full Playwright run of `radar-women.biom.kg`: both languages,
   free navigation, printing. Separately, the mobile answer widget
   (`Question.tsx`, the width < 1024 branch), which was not checked last time.

### Result check

- «Сельское хозяйство»: go through the indicator choosing the **best in meaning**
  option everywhere; the average score should come out 3.0 (currently 2.0 with "all 3s").
- «Механизмы миростроительства»: check whether the two YES/NO questions flip
  the indicator across a risk zone boundary.
- Гендер: after deleting the question, the indicator has 7 questions. Gaps in `ord`
  (5 and 8) are harmless: the frontend numbers questions by array position
  (`Questions.tsx`, `num: index + 1`); `ord` is used only for sorting.

---

## 7. Numbering mismatches

Numbers in the expert's document do not match `ord` in the database in places; matching was done by
question text:

| Question | Expert's number | In the database |
|---|---|---|
| Участвуют ли женщины в планировании действий при ЧС | 8 | `ord=9` |
| Существуют ли совместные инициативы разных групп жителей | 6 | `ord=7` |
| Способны ли местные власти, жители и организации совместно реагировать | 7 | `ord=8` |

---

## 8. Out of scope

- **23 questions** keep digit labels with the explanation inside the question text:
  «Окружающая среда» (Environment): 8, «Вода, санитария, гигиена» (Water, sanitation, hygiene): 6, «Среда населённых пунктов» (Settlement environment): 5,
  «Потенциал сообщества»: 3, «Ирригация»: 1. The expert did not review them.
- Of these, **11 questions** cannot be switched to word buttons mechanically even if
  we wanted to: their explanation is given as a range («0, 1 — нет», «0-1 критически
  недостаточно») or only by the scale ends («0 — совершенно не готово, 3 — хорошо
  подготовлено»). List: Окружающая среда ord 5, 6, 7, 8, 9; Вода/санитария ord 10;
  Среда населённых пунктов ord 3, 6, 8, 9, 16. Two more questions of the same form,
  Сельское хозяйство ord 1 and Потенциал сообщества ord 7, are resolved in §2 and §1.2.
- Separate «Скачать рус / Скачать кырг» buttons (§4.5).
- Automatic deploy (GitHub Actions): as before, deploy is manual.
