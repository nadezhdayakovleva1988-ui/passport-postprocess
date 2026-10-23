import json
import re

labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}

RE_BP_START = re.compile(
    r"^(С\.|Д\.|П\.|Г\.|ГОР\.|Р\.П\.|ПОС\.|СЕЛО|ДЕРЕВНЯ|ДЕР\.|СТАНИЦА|"
    r"ХУТОР|АУЛ|ПГТ|РАБ\.|ПОСЕЛОК|С\.П\.|ПГТ\.|СТ-ЦА|СТ\.|ПОСЁЛОК|"
    r"ПОС\.|Г\.|МЕСТ\.|ПГТ\.|СЕЛ\.)",
    re.IGNORECASE,
)

no_prefix = 0
for d in labels.values():
    bp = (d["fields"]["Birth_place_ru"] or "").strip().upper()
    if not RE_BP_START.match(bp):
        no_prefix += 1
        if no_prefix <= 20:
            print(f"{d['doc_id']}: {bp!r}")

print(f"\nвсего без префикса: {no_prefix}")