# Журнал экспериментов

Формат: `[дата] [коммит] [что] → good/bad`

## Текущее состояние (baseline)
- `postprocess.py`: char_conf=0.80, char_conf_names=0.90, char_conf_org=?, char_conf_bp=?
- `evaluate.py` на train: **good=1483, bad=174**
- Файлы: answers_train.jsonl (перегенерировать после правок)

## История

### 2026-10-23 — старт
- Закоммитил текущее состояние.
- Метрики: good=1483, bad=174.
- Что сделано: char_conf_names=0.90 (имена).
- Что НЕ сделано: check_org, форматы, issue_before_20, Middle_name_ru.

## Очередь задач (TODO)
- [ ] `tune_org.py` — подобрать `char_conf_org`
- [ ] `check_org.py` — проверить `no_kw` на train (безопасность `check_org`)
- [ ] `check_formats.py` — проверить, не строгие ли `RE_LIC`/`RE_DATE`
- [ ] `issue_before_20` — проверить ложные срабатывания
- [ ] `Middle_name_ru` — решение: reject (оставить) или принимать null
- [ ] Финальный `evaluate.py` → `answers.jsonl` для test
- [ ] Отчёт `report.md`

## Отклонённые идеи (не повторять)
- `bad_frac` вместо `min_char` — bad вырос 193→398, откатил.
- `RE_BP_START` — 356 правильных Birth_place_ru без префикса, отклонит их.
- `REGION_MARKERS` — 208 правильных без региона, отклонит их.
- `char_conf_bp=0.92` — bad=123, good=1460; размен плохой, оставил 0.80.