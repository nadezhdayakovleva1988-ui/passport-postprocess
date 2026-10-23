import json
import postprocess as pp

codes = pp.load_subdivisions()
print(f"всего кодов в CSV: {len(codes)}")
print(f"примеры кодов из CSV: {list(codes)[:5]}")

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}

mismatch_fmt = 0
for p in preds:
    v = (p.get("viz") or {}).get("Issue_organisation_code")
    if not v or not v.get("lines"): continue
    pred_code = v["lines"][0]["text"].strip()
    gold_code = labels[p["doc_id"]]["fields"]["Issue_organisation_code"]
    if pred_code == gold_code and pred_code not in codes:
        # код правильный по разметке, но не найден в CSV
        print(f"НЕ НАЙДЕН: doc={p['doc_id']} code={pred_code!r} len={len(pred_code)}")
        mismatch_fmt += 1
        if mismatch_fmt >= 10: break
print(f"итого правильных, но не найденных: {mismatch_fmt}")