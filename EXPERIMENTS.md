# Журнал экспериментов

### 2026-10-23 — char_conf_org
- tune_org.py: 0.80→174, 0.82→167, 0.85→153, 0.88→146, 0.90→143, 0.92→133
- Выбрал 0.90: good=1469 bad=143 (−31 bad, −14 good)
- Коммит: <0bf53c6>

### 2026-10-23 — char_conf_org vs check_org
- Только char_conf_org=0.90: good=1469 bad=143 (−14 good, −31 bad) ✓ ОСТАВИТЬ
- Только check_org (расширенный ORG_KEYWORDS): good=1435 bad=168 (−48 good, −6 bad) ✗ УБРАТЬ
- Оба: good=1421 bad=139 (−62 good, −35 bad) — хуже, чем только char_conf_org
- Решение: оставить char_conf_org=0.90, check_org убрать из decide()
- Коммит: <a89b1a9>

### 2026-10-23 — char_conf_org=0.92
- 0.90: good=1469 bad=143
- 0.92: good=1464 bad=133 (−5 good, −10 bad) ✓ ОСТАВИТЬ
- Issue_organization_ru: 32 → 25
- Коммит: <71fc258>

## Текущее состояние (baseline)
- `postprocess.py`: char_conf=0.80, char_conf_names=0.90, char_conf_org=0.90
- `evaluate.py` на train: **good=1464, bad=133**
- Ошибки по полям: BLast_name_ru=22, First_name_ru=11, Middle_name_ru=12, Birth_place_ru=61, Issue_date=3, Issue_organisation_code=3, Licence_number=7, Issue_organization_ru=32

## Что сделано
- [x] MRZ-парсер исправлен (YYMMDD, день/месяц не перепутаны) — был баг, good 109→1494
- [x] char_conf_names=0.90 для имён — bad 193→174
- [x] char_conf=0.80 для остальных
- [x] Справочник: фолбэк на train-коды (19 уникальных кодов, 42 документа)

## Отклонённые идеи (НЕ повторять)
- `bad_frac` вместо `min_char` — bad вырос 193→398, откатил
- `RE_BP_START` (префикс нас. пункта) — 356 правильных Birth_place_ru без префикса
- `REGION_MARKERS` (регион в тексте) — 208 правильных без региона
- `char_conf_bp=0.92` — bad=123, good=1460; размен плохой, оставил 0.80

## Очередь задач (TODO)
- [ ] `tune_org.py` — подобрать `char_conf_org` (Issue_organization_ru, 62 ошибки)
- [ ] `check_org.py` — проверить `no_kw` на train (безопасность check_org)
- [ ] `check_formats.py` — проверить, не строгие ли RE_LIC/RE_DATE
- [ ] `issue_before_20` — проверить ложные срабатывания
- [ ] `Middle_name_ru` — решение: оставить reject или принимать null
- [ ] Финальный `evaluate.py` → `answers.jsonl` для test
- [ ] Отчёт `report.md`

## Цель
- `bad ≤ 100` при `good ≥ 1400` → на test ожидаемо ~933 good, ≤67 bad
- Если `bad ≤ 50` — совсем хорошо