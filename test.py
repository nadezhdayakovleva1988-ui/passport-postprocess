import json
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}

def check_digit(s):
    weights = [7, 3, 1]
    total = 0
    for i, ch in enumerate(s):
        if ch.isdigit(): v = int(ch)
        elif ch.isalpha(): v = ord(ch) - ord('A') + 10
        else: v = 0
        total += v * weights[i % 3]
    return total % 10

cnt_total = cnt_bad_check = 0
for p in preds:
    m = pp.parse_mrz(p)
    if m is None or "Birth_date" not in m: continue
    f = pp.extract_fields(p)
    if f["Birth_date"] is None: continue
    gold = labels[p["doc_id"]]["fields"]["Birth_date"]
    mrz_ok = pp._norm(m["Birth_date"]) == pp._norm(gold)
    viz_ok = pp._norm(f["Birth_date"]["text"]) == pp._norm(gold)
    if viz_ok and not mrz_ok:
        cnt_total += 1
        l2 = p["mrz"]["lines"][1]["text"]
        if len(l2) < 20 or not l2[19].isdigit() or check_digit(l2[13:19]) != int(l2[19]):
            cnt_bad_check += 1
            print(f"doc={p['doc_id']} MRZ={l2[13:19]!r} check={l2[19]!r} expected={check_digit(l2[13:19])}")

print(f"\nвсего 'viz прав, MRZ ошибается': {cnt_total}")
print(f"из них с несошедшейся контрольной: {cnt_bad_check}")