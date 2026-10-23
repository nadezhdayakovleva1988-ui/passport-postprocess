import json
import collections
import postprocess as pp

preds = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")}
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}
codes = pp.load_subdivisions(train_labels="data/train_labels.jsonl")

errors = []
for doc_id, p in preds.items():
    dec, reason, fields = pp.decide(p, codes)
    if dec != "accept": continue
    gold = labels[doc_id]["fields"]
    wrong = [k for k in pp.FIELDS if pp._norm(fields.get(k)) != pp._norm(gold[k])]
    if wrong:
        f = pp.extract_fields(p)
        errors.append({
            "doc_id": doc_id,
            "source": p.get("source"),
            "quality": p.get("quality"),
            "wrong_fields": wrong,
            "min_chars": {k: round(f[k]["min_char"], 3) if f[k] else None for k in wrong},
            "confs": {k: round(f[k]["conf"], 3) if f[k] else None for k in wrong},
            "mrz": bool(p.get("mrz")),
        })

print(f"всего ошибочных принятых: {len(errors)}\n")

# 1. распределение по source
by_src = collections.Counter(e["source"] for e in errors)
print("по source:", dict(by_src))

# 2. распределение по wrong_fields (одиночные vs комбинации)
by_field = collections.Counter()
for e in errors:
    for k in e["wrong_fields"]:
        by_field[k] += 1
print("\nпо полям:", dict(by_field))

# 3. сколько ошибочных имеют mrz
print(f"\nс MRZ: {sum(e['mrz'] for e in errors)} / {len(errors)}")

# 4. min_char ошибочных полей: перцентили
all_min = sorted(m for e in errors for m in e["min_chars"].values() if m is not None)
if all_min:
    n = len(all_min)
    print(f"\nmin_char ошибочных полей (n={n}):")
    print(f"  p10={all_min[int(n*0.10)]:.3f} p25={all_min[int(n*0.25)]:.3f} "
          f"p50={all_min[int(n*0.50)]:.3f} p75={all_min[int(n*0.75)]:.3f} "
          f"p90={all_min[int(n*0.90)]:.3f}")

# 5. sharpness / glare у ошибочных
sharp = sorted(e["quality"]["sharpness"] for e in errors if e["quality"])
glare = sorted(e["quality"]["glare"] for e in errors if e["quality"])
if sharp:
    n = len(sharp)
    print(f"\nsharpness (n={n}): p10={sharp[int(n*0.10)]:.1f} p50={sharp[int(n*0.50)]:.1f} p90={sharp[int(n*0.90)]:.1f}")
if glare:
    n = len(glare)
    print(f"glare (n={n}): p10={glare[int(n*0.10)]:.3f} p50={glare[int(n*0.50)]:.3f} p90={glare[int(n*0.90)]:.3f}")

# 6. 10 примеров с ошибочным Birth_place_ru
print("\n10 примеров Birth_place_ru:")
cnt = 0
for e in errors:
    if "Birth_place_ru" in e["wrong_fields"]:
        p = preds[e["doc_id"]]
        viz = (p.get("viz") or {}).get("Birth_place_ru")
        pred_text = " ".join(l["text"] for l in viz["lines"]) if viz and viz.get("lines") else None
        print(f"  {e['doc_id']} src={e['source']} min_char={e['min_chars'].get('Birth_place_ru')} "
              f"pred={pred_text!r} gold={labels[e['doc_id']]['fields']['Birth_place_ru']!r}")
        cnt += 1
        if cnt >= 10: break