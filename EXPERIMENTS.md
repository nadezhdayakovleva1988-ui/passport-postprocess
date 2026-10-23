# Журнал экспериментов

Формат: `[дата] [что] → good/bad`

## Текущее состояние (baseline)
- `postprocess.py`: char_conf=0.80, char_conf_names=0.90
- `evaluate.py` на train: **good=1483, bad=174**
- Ошибки по полям: Birth_place_ru=64, Issue_organization_ru=62,
  Last_name_ru=23, Middle_name_ru=12, First_name_ru=11,
  Licence_number=7, Issue_date=4, Issue_organisation_code=3

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