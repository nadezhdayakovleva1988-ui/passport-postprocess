import json
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}
codes = pp.load_subdivisions(train_labels="data/train_labels.jsonl")

for cc in [0.80, 0.85, 0.88, 0.90, 0.92, 0.95]:
    pp.TH["char_conf"] = cc
    good = bad = 0
    for p in preds:
        dec, _, fields = pp.decide(p, codes)
        if dec != "accept": continue
        gold = labels[p["doc_id"]]["fields"]
        if all(pp._norm(fields.get(k)) == pp._norm(gold[k]) for k in pp.FIELDS):
            good += 1
        else:
            bad += 1
    print(f"char_conf={cc:.2f}: good={good} bad={bad}")