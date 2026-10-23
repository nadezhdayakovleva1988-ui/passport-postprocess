# Постобработка OCR паспортов РФ

## Запуск
python3 postprocess.py data/test_predictions.jsonl answers.jsonl

Требования: Python 3.8+, только стандартная библиотека. CPU, без интернета.

## Файлы
- postprocess.py — каскад правил (главный скрипт)
- analyze_train.py — диагностика train (для отчёта)
- tune.py — подбор порогов на train
- report.md — отчёт