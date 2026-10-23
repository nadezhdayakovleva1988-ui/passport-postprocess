import json
import collections

labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}
endings = collections.Counter()
for d in labels.values():
    bp = (d["fields"]["Birth_place_ru"] or "").strip().upper()
    last = bp.split()[-1] if bp else ""
    endings[last] += 1

print("топ-20 окончаний Birth_place_ru в gold:")
for e, c in endings.most_common(20):
    print(f"  {e!r}: {c}")