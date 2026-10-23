import json
import postprocess as pp

for line in open("data/train_predictions.jsonl", encoding="utf-8"):
    p = json.loads(line)
    if p["doc_id"] == "tr_00270":
        f = pp.extract_fields(p)
        print(f"Licence_number = {f['Licence_number']['text']!r}")
        print(f"RE_LIC match = {bool(pp.RE_LIC.match(f['Licence_number']['text']))}")
        dec, reason, _ = pp.decide(p, pp.load_subdivisions(train_labels="data/train_labels.jsonl"))
        print(f"decision = {dec}, reason = {reason}")
        break