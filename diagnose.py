import json
import collections
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
codes = pp.load_subdivisions(train_labels="data/train_labels.jsonl")

# 1. сколько документов отклоняется по каждому правилу
reasons = collections.Counter()
for p in preds:
    dec, reason, _ = pp.decide(p, codes)
    if dec == "reject":
        reasons[reason] += 1

print("=== причины reject ===")
for r, c in reasons.most_common():
    print(f"  {r:40s} {c:5d}")

# 2. распределение min_char по полям
print("\n=== min_char по полям (перцентили) ===")
by_field = collections.defaultdict(list)
for p in preds:
    f = pp.extract_fields(p)
    for k, v in f.items():
        if v is not None:
            by_field[k].append(v["min_char"])

for k in pp.FIELDS:
    vals = sorted(by_field[k])
    if not vals: continue
    n = len(vals)
    p10 = vals[int(n * 0.10)]
    p25 = vals[int(n * 0.25)]
    p50 = vals[int(n * 0.50)]
    p75 = vals[int(n * 0.75)]
    p90 = vals[int(n * 0.90)]
    print(f"  {k:28s} n={n:4d} p10={p10:.3f} p25={p25:.3f} p50={p50:.3f} p75={p75:.3f} p90={p90:.3f}")

# 3. распределение conf по полям
print("\n=== conf по полям (перцентили) ===")
by_conf = collections.defaultdict(list)
for p in preds:
    f = pp.extract_fields(p)
    for k, v in f.items():
        if v is not None:
            by_conf[k].append(v["conf"])

for k in pp.FIELDS:
    vals = sorted(by_conf[k])
    if not vals: continue
    n = len(vals)
    print(f"  {k:28s} n={n:4d} p10={vals[int(n*0.10)]:.3f} p50={vals[int(n*0.50)]:.3f} p90={vals[int(n*0.90)]:.3f}")