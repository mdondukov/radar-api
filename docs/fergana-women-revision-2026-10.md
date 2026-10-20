# «Женщины Ферганы» (Women of Fergana) - Kyrgyz proofreading and comments (October 2026)

Source: the `radar_women_review/` file package received on 16 October 2026:

- `Правки Радар_Гулмайрам.docx` - the same document as in the September revision
  (edits by Kirilenko Anna), plus 9 comments by the author «Admin» dated 3 September.
  Anna's edits are already applied (`fergana-women-revision-2026-09.md`); the comments
  did not make it into the September specification.
- Ten `*_кырг.docx` files and `Ирригационные ресурсы и инфраструктура.docx` -
  proofreading of the Kyrgyz text by a native speaker (Nursultan, 4-6 September). This is
  the proofreading required by §3 of the September specification. He went through the live
  site in the Russian version with the Kyrgyz mirror and edited the Kyrgyz part in
  track-changes mode.

---

## 1. Decisions on the «Admin» comments

| Comment | Decision |
|---|---|
| Сельское хозяйство (Agriculture), questions 6, 10-13: «0 должно значить плохо» ("0 should mean bad") | Already resolved in September: word buttons, ordered by ascending weight |
| Климатические риски (Climate risks), question 2 «Конфликты из-за земли» | **Scoring error, fixed** (§2.1) |
| Expand ООПТ (specially protected natural areas) in the recommendations | Fixed in both languages (§2.2) |
| Language switcher at the top of each block | **Not doing.** Questions and answers are already shown in both languages at once; the information and recommendation blocks have their own switcher |
| Irrigation icon is the same as drinking water | Fixed (§4) |
| Free order of going through the blocks | **Not doing**, see below |

**Block order.** Free navigation was implemented on 3 September and deliberately restricted
on 4 September. Reason: a user jumped straight to the last indicator, answered, pressed
«Далее» twice and landed on a radar built from eight empty indicators counted as zero.
Current rule:

- backward - free, including from a partially filled indicator (noticed a mistake in a
  previous block - went back, fixed it, moved on);
- forward - only up to the furthest step already reached, so going back does not take
  away the way forward;
- the radar opens only after answers in all nine indicators and names the unfilled ones.

Reply to the expert: blocks can be rechecked and corrected in any order, but the first pass
must go in sequence, otherwise the final chart will be unreliable.

---

## 2. Content: score and term fixes

### 2.1. «Возникают ли конфликты из-за доступа к земле или изменения ее состояния?»

Before: `нет` 0 · `частично` 1 · `в целом, да` 2 · `активно` 3 - the absence of conflicts
gave maximum vulnerability. After (ordered by ascending weight, as everywhere else):

`активно` 0 · `в целом, да` 1 · `частично` 2 · `нет` 3

The options of this question have no recommendations, so the flip does not affect them.

### 2.2. ООПТ

- RU, high risk zone text of «Окружающей среды» (Environment): first mention -
  «Взаимодействие с особо охраняемыми природными территориями (ООПТ)», abbreviation
  after that.
- RU, recommendation to the question about the presence of ООПТ: «Взаимодействие с особо
  охраняемыми природными территориями.» - following Nursultan's Kyrgyz edit, where the
  abbreviation in the recommendation is also expanded.
- KY - the same with «Өзгөчө коргоого алынган жаратылыш аймактары (ӨКАЖА)».
- In the question text itself the abbreviation is introduced in parentheses and stays.

---

## 3. Kyrgyz proofreading

### 3.1. What was applied

All of Nursultan's edits in the text of questions, answer options, introductions,
descriptions, risk zone texts and recommendations - 99 Kyrgyz fields. Edits were transferred
by a word-level "before/after" comparison of each paragraph of the document. Line breaks
inside texts are preserved. The Russian text was not changed.

Typos in the document itself were fixed:

- «бирдейкамсыз», «ыкмаларыжана» - missing spaces;
- «Жайылма токойлорЖайылма» - duplicate;
- «…коргоо. ШамалТалаалар» - extra word;
- «аТабигый» - extra letter;
- the subheading «Топурак коргоочу токой өстүрүү жана микроклимат.» is again on a
  separate line.

Indicator names:

- `Курчап турган чөйрө` → `Айлана-чөйрө`;
- `Тынчтык курулуш механизмдери` → `Тынчтык куруу механизмдери`.

UI strings (`radar-women/src/i18n/messages-ky.json`):

- «Далее» → «Кийинки» (was «Андан ары»);
- average score → «Орточо балыңыз: 3төн {result}»;
- the hint under «Далее»;
- three texts on the radar page.

### 3.2. Global replacements across all Kyrgyz content

Only where Nursultan changed a term always and without exceptions:

| Before | After | Occurrences outside his edits |
|---|---|---|
| жайык (токой, зона, экосистема) | жайылма | 3 |
| жарка | жыра | 3 |
| токой коргоо алкактарын | коргоочу токой тилкелерин | 1 |
| стихиялуу (таштандылоо) | башаламан | 3 |
| аялуу | аярлуу | 8 |

### 3.3. What was not applied and why

- **Region texts** (the «Дыйканчылык ойдуң зонасы» zone, impact on Jalal-Abad).
  The region tree is copied from the `zhashyl-climate` project
  (`copy_regions_to_fergana.py`); this is another team's content, we do not change their
  translation.
- **Kyrgyz mirror of radar headings, buttons and captions in the Russian version.**
  The translations he wrote under these elements were taken into the Kyrgyz locale, but in
  the Russian version these elements are not duplicated: the mirror was requested only for
  questions and answers.

### 3.4. Questions for Nursultan

1. **Name of «Сельского хозяйства» (Agriculture).** In the block file it is «Айыл чарба»,
   in the radar file «Айыл чарбасы». «Айыл чарбасы» was kept.
2. **«СЭӨПна (ПСЭР)»** - applied as in the document; the «-на» ending should be checked. The
   other recommendations still have «ПСЭРге», «ПСЭРди», «(ПСЭР)» - a single form is needed.
3. **Terms he did not change everywhere** - not replaced throughout the text, a decision is
   needed:
   - `адаптация` → `ыңгайлашуу`: replaced in questions and recommendations, but in his own
     insertion he left «начар адаптациялык инфраструктура». 9 occurrences remain.
   - `жамаат` → `коомчулук`: replaced in questions, but left «жергиликтүү
     жамааттардын», «Жамааттык микрокорук». 8 remain.
   - `уязвимдүүлүк`: replaced sometimes with «алсыздык», sometimes with «аярлуулук». 2 remain.
   - `алкак`: «коргоочу жашыл алкактар», «өрткө каршы алкактар» - whether to change to
     «тилке» («чөл алкагы» etc. in the sense of a natural zone are not touched).
4. **What he did not see.** The proofreading followed a single pass through the site, so it
   does not cover:
   - texts of other risk zones: in six blocks he got «3 из 3», meaning he saw only the
     low zone text;
   - recommendations for answers he did not choose.
5. **His comment "no recommendations for the three new blocks".** This is not a bug: the
   Гендер (Gender), Климатические риски and Миростроительство (Peacebuilding) blocks do have
   recommendations (12, 6 and 12), but they are tied to answers with weight 0-2, and he chose
   the best option everywhere. To see them, these blocks have to be completed with poor
   answers.

### 3.5. Nursultan's answers (20 October 2026)

1. The indicator name is «Айыл чарба». The «айыл чарбасы» forms inside description
   sentences stay.
2. Single form - «СЭӨП»: «ПСЭРге» → «СЭӨПна», «ПСЭРди» → «СЭӨПны», «(ПСЭР)» →
   «(СЭӨП)». Where it said «СЭӨПна (ПСЭР)», the parenthesis was removed. The Russian text
   does not change.
3. `уязвимдүүлүк` → `аярлуулук` (2 places). `адаптация`, `жамаат`, `алкак` stay.
4. He is going through the texts of other risk zones and the recommendations for worse
   answers separately; results in the next round.

---

## 4. Interface

Icon of «Ирригационные ресурсы и инфраструктура» (Irrigation resources and infrastructure)
in the navigation: `GiTap` (a water tap, reads as drinking water) → `GiPlantWatering`
(watering a plant). The illustration on the block result page (drip irrigation) fits the
topic and stays.

---

## 5. Rollout order

1. The §3.4 question list goes to Nursultan; answers are applied before the rollout or in a
   separate round.
2. `radar-api`: branch `content/ky-proofreading-2026-10` → CI → merge → «Seed
   fergana-women content» with the `seed` confirmation (seed and region copy).
   No image deploy is needed - only data changes.
3. `radar-women`: branch `content/ky-proofreading-2026-10` → CI → merge → Deploy.
4. Production check:
   - Kyrgyz version - indicator names, «Кийинки», average score;
   - the question about land conflicts: «нет» gives 3;
   - the new irrigation icon.
