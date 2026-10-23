import json
import postprocess as pp

labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}
preds  = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]

for arg in (None, "data/train_labels.jsonl"):
    codes = pp.load_subdivisions(train_labels=arg)
    rej_code_unknown = 0
    for p in preds:
        dec, reason, _ = pp.decide(p, codes)
        if reason == "code_unknown":
            rej_code_unknown += 1
    print(f"train_labels={arg}: reject по code_unknown = {rej_code_unknown}")