import json
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}
codes = pp.load_subdivisions(train_labels="data/train_labels.jsonl")

for bf in [0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 0.10]:
    pp.TH["bad_frac"] = bf
    good = bad = 0
    for p in preds:
        dec, _, fields = pp.decide(p, codes)
        if dec != "accept":
            continue
        gold = labels[p["doc_id"]]["fields"]
        if all(pp._norm(fields.get(k)) == pp._norm(gold[k]) for k in pp.FIELDS):
            good += 1
        else:
            bad += 1
    print(f"bad_frac={bf:.2f}: good={good} bad={bad}")