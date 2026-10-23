import json
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
codes = pp.load_subdivisions(train_labels="data/train_labels.jsonl")

# Сколько документов имеют min_char < 0.80 хотя бы в одном поле
low_char_docs = 0
low_char_field = {}
for p in preds:
    f = pp.extract_fields(p)
    if any(v is None for v in f.values()):
        continue
    bad = [k for k, v in f.items() if v["min_char"] < 0.80]
    if bad:
        low_char_docs += 1
        for k in bad:
            low_char_field[k] = low_char_field.get(k, 0) + 1

print(f"документов с min_char < 0.80 хотя бы в одном поле: {low_char_docs}/{len(preds)} ({low_char_docs/len(preds):.1%})")
print("по полям:")
for k, c in sorted(low_char_field.items(), key=lambda x: -x[1]):
    print(f"  {k:28s} {c}")