"""analyze_train.py — диагностика train для отчёта."""
import json, csv, collections
import postprocess as pp

FIELDS = pp.FIELDS

def load(path):
    with open(path, encoding="utf-8") as f:
        return {d["doc_id"]: d for d in map(json.loads, f)}

def main():
    preds  = load("data/train_predictions.jsonl")
    labels = load("data/train_labels.jsonl")
    codes  = pp.load_subdivisions()

    # 1. доля ошибок по полям (среди ВСЕХ документов)
    err = collections.Counter()
    n = len(preds)
    for doc_id, p in preds.items():
        f = pp.extract_fields(p)
        gold = labels[doc_id]["fields"]
        for k in FIELDS:
            if f[k] is None:
                err[k + "_missing"] += 1
            elif pp._norm(f[k]["text"]) != pp._norm(gold[k]):
                err[k] += 1
    print(f"документов: {n}")
    for k in FIELDS:
        e = err[k]; m = err[k + "_missing"]
        print(f"  {k:28s} ошибок={e:5d} ({e/n:.1%})  null={m:5d}")

    # 2. точность поля vs min(char_conf) — по бинам
    print("\nточность поля по min(char_conf):")
    bins = collections.defaultdict(lambda: [0, 0])
    for doc_id, p in preds.items():
        f = pp.extract_fields(p)
        gold = labels[doc_id]["fields"]
        for k in FIELDS:
            if f[k] is None: continue
            b = round(f[k]["min_char"] * 10) / 10
            bins[b][1] += 1
            bins[b][0] += (pp._norm(f[k]["text"]) == pp._norm(gold[k]))
    for b in sorted(bins):
        ok, tot = bins[b]
        print(f"  min_char ~{b:.1f}: точность {ok/tot:.1%} (n={tot})")

    # 3. справочник: сколько кодов из train отсутствует
    present_wrong = missing_correct = missing_wrong = 0
    for doc_id, p in preds.items():
        v = (p.get("viz") or {}).get("Issue_organisation_code")
        if not v or not v.get("lines"): continue
        pred_code = v["lines"][0]["text"].strip()
        gold_code = labels[doc_id]["fields"]["Issue_organisation_code"]
        in_ref = pred_code in codes
        if pred_code != gold_code and not in_ref: missing_wrong  += 1
        elif pred_code != gold_code and in_ref:  present_wrong += 1
        elif pred_code == gold_code and not in_ref: missing_correct += 1
    print(f"\nсправочник: missing_wrong={missing_wrong} "
          f"present_wrong={present_wrong} missing_correct={missing_correct}")

    # 4. MRZ: доля документов с MRZ, доля расхождений viz<->MRZ
    mrz_present = mrz_mismatch = 0
    for doc_id, p in preds.items():
        m = pp.parse_mrz(p)
        if m is None: continue
        mrz_present += 1
        f = pp.extract_fields(p)
        if pp.check_mrz(p, f): mrz_mismatch += 1
    print(f"MRZ: есть у {mrz_present}/{n} ({mrz_present/n:.1%}), "
          f"расхождений с viz: {mrz_mismatch}")

    # 5. точность по source
    by_src = collections.defaultdict(lambda: [0, 0])
    for doc_id, p in preds.items():
        src = p.get("source", "web")
        f = pp.extract_fields(p)
        gold = labels[doc_id]["fields"]
        ok = all(f[k] is not None and pp._norm(f[k]["text"]) == pp._norm(gold[k])
                 for k in FIELDS)
        by_src[src][1] += 1
        by_src[src][0] += ok
    print("\nточность по source:")
    for s, (ok, tot) in by_src.items():
        print(f"  {s:12s}: {ok/tot:.1%} (n={tot})")

if __name__ == "__main__":
    main()