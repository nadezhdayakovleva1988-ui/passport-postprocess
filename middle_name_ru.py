import json
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}

empty_gold = 0
filled_gold = 0
for p in preds:
    v = (p.get("viz") or {}).get("Middle_name_ru")
    if v and v.get("lines"): continue
    gold = labels[p["doc_id"]]["fields"]["Middle_name_ru"]
    if not gold or gold.strip() == "":
        empty_gold += 1
    else:
        filled_gold += 1
        if filled_gold <= 5:
            print(f"{p['doc_id']}: gold Middle_name_ru = {gold!r}")

print(f"\nviz null, gold пусто:  {empty_gold}")
print(f"viz null, gold заполнено: {filled_gold}")