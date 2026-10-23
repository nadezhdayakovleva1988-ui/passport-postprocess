import json
import postprocess as pp

preds = [json.loads(l) for l in open("data/train_predictions.jsonl", encoding="utf-8")]
labels = {json.loads(l)["doc_id"]: json.loads(l) for l in open("data/train_labels.jsonl", encoding="utf-8")}
codes = pp.load_subdivisions(train_labels="data/train_labels.jsonl")

import types

def make_check_confidence(cn, cc, co, cb):
    def check_confidence(f, source):
        extra = pp.TH["mobile_extra"] if source in ("mobile", "mobile_v2") else 0.0
        for name, v in f.items():
            if v is None: return f"missing_{name}"
            if v["conf"] < pp.TH["conf"] + extra: return f"low_conf_{name}"
            if name in pp.NAME_FIELDS: th = cn
            elif name == "Issue_organization_ru": th = co
            elif name == "Birth_place_ru": th = cb
            else: th = cc
            if v["min_char"] < th + extra:
                return f"low_char_{name}"
        return None
    return check_confidence

orig = pp.check_confidence
for cb in [0.80, 0.82, 0.85, 0.88, 0.90, 0.92]:
    pp.check_confidence = make_check_confidence(
        pp.TH["char_conf_names"], pp.TH["char_conf"], 0.85, cb
    )
    good = bad = 0
    for p in preds:
        dec, _, fields = pp.decide(p, codes)
        if dec != "accept": continue
        gold = labels[p["doc_id"]]["fields"]
        if all(pp._norm(fields.get(k)) == pp._norm(gold[k]) for k in pp.FIELDS):
            good += 1
        else:
            bad += 1
    print(f"char_conf_bp={cb:.2f}: good={good} bad={bad}")

pp.check_confidence = orig