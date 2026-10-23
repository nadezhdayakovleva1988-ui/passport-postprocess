import json
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}

shown = 0
for p in preds:
    m = pp.parse_mrz(p)
    if m is None: continue
    f = pp.extract_fields(p)
    err = pp.check_mrz(p, f)
    if err and "Birth_date" in err:
        lines = [l["text"] for l in p["mrz"]["lines"]]
        viz_birth = f["Birth_date"]["text"] if f["Birth_date"] else None
        gold_birth = labels[p["doc_id"]]["fields"]["Birth_date"]
        print(f"doc={p['doc_id']}")
        print(f"  L1 ({len(lines[0])}): {lines[0]!r}")
        print(f"  L2 ({len(lines[1])}): {lines[1]!r}")
        print(f"  parsed Birth_date = {m.get('Birth_date')!r}")
        print(f"  viz Birth_date    = {viz_birth!r}")
        print(f"  gold Birth_date   = {gold_birth!r}")
        print(f"  L2[13:19]         = {lines[1][13:19]!r}")
        print()
        shown += 1
        if shown >= 8: break