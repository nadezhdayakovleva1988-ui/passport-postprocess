import json
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}

cnt = 0
for p in preds:
    m = pp.parse_mrz(p)
    if m is None or "_mrz_number" not in m: continue
    f = pp.extract_fields(p)
    if f["Licence_number"] is None: continue
    viz_num = "".join(c for c in f["Licence_number"]["text"] if c.isdigit())[-6:]
    if viz_num != m["_mrz_number"][-6:]:
        gold = labels[p["doc_id"]]["fields"]["Licence_number"]
        mrz_ok = pp._norm(m["_mrz_number"][-6:]) == pp._norm("".join(c for c in gold if c.isdigit())[-6:])
        viz_ok = pp._norm(f["Licence_number"]["text"]) == pp._norm(gold)
        print(f"{p['doc_id']} mrz={m['_mrz_number'][-6:]!r} viz={f['Licence_number']['text']!r} gold={gold!r} "
              f"mrz_ok={mrz_ok} viz_ok={viz_ok}")
        cnt += 1
        if cnt >= 10: break