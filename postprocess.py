"""postprocess.py — каскад правил для OCR паспортов РФ.

Запуск:
    python postprocess.py data/test_predictions.jsonl answers.jsonl

Требования: Python 3.8+, только stdlib. CPU, без интернета.
"""
import json
import re
import csv
import sys
from datetime import date, datetime

REF_DATE = date(2026, 10, 1)

FIELDS = [
    "Last_name_ru", "First_name_ru", "Middle_name_ru",
    "Sex_ru", "Birth_date", "Birth_place_ru",
    "Issue_date", "Issue_organisation_code",
    "Licence_number", "Issue_organization_ru",
]

# ---- пороги: подобраны на train (см. tune.py и report.md) ----
TH = {
    "conf":          0.90,   # средняя conf поля
    "char_conf":     0.80,   # min char_conf для коротких полей (имена, даты, номер, код)
    "char_conf_names": 0.90,   # min char_conf для имён (строже)
    "char_conf_org":   0.92,
    "bad_frac":      0.01,   # доля символов с char_conf < 0.5 для длинных полей
    "sharpness":     None,   # мин. sharpness (None = не режем)
    "glare":         None,   # макс. glare (None = не режем)
    "mobile_extra":  0.00,   # доп. ужесточение для mobile/mobile_v2
}

# ------------------------- справочник -------------------------
def load_subdivisions(path="reference/subdivisions.csv",
                      train_labels=None):
    """Множество кодов. Если справочник неполный — дополняем кодами из train."""
    codes = set()
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = (row.get("code") or "").strip().strip("\r\n\t \xa0")
            if code:
                codes.add(code)
    if train_labels:
        try:
            with open(train_labels, encoding="utf-8") as f:
                for line in f:
                    d = json.loads(line)
                    c = (d.get("fields") or {}).get("Issue_organisation_code")
                    if c:
                        codes.add(c.strip())
        except FileNotFoundError:
            pass
    return codes

# ------------------------- извлечение -------------------------
def extract_fields(pred):
    viz = pred.get("viz") or {}
    out = {}
    for name in FIELDS:
        v = viz.get(name)
        if not v or not v.get("lines"):
            out[name] = None
            continue
        text = " ".join(l["text"] for l in v["lines"]).strip()
        char_confs = [c for l in v["lines"] for c in l.get("char_conf", [])]
        n = len(char_confs)
        bad_frac = sum(1 for c in char_confs if c < 0.5) / n if n else 0.0
        out[name] = {
            "text": text,
            "conf": float(v.get("conf") or 0.0),
            "min_char": min(char_confs) if char_confs else 1.0,
            "bad_frac": bad_frac,
        }
    return out

# ------------------------- регэкспы -------------------------
RE_DATE  = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
RE_CODE  = re.compile(r"^\d{3}-\d{3}$")
RE_SEX   = re.compile(r"^(МУЖ|ЖЕН)\.?$")
RE_NAME  = re.compile(r"^[А-Яа-яЁё\-\s]+$")
RE_ORG   = re.compile(r"^[А-Яа-яЁё0-9\-\s\"'«».,№]+$")
RE_LIC   = re.compile(r"^\d{2}\s+\d{2}\s+\d{6}$")

def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y").date()
    except Exception:
        return None

# ------------------------- проверки -------------------------
def check_formats(f):
    if not RE_DATE.match(f["Issue_date"]["text"]):               return "issue_date_fmt"
    if not RE_DATE.match(f["Birth_date"]["text"]):               return "birth_date_fmt"
    if not RE_CODE.match(f["Issue_organisation_code"]["text"]):  return "code_fmt"
    if not RE_SEX.match(f["Sex_ru"]["text"]):                    return "sex_fmt"
    if not RE_LIC.match(f["Licence_number"]["text"]):            return "licence_fmt"
    return None



RE_ORG_TRUNC_END = re.compile(r"\s(В|ПО)\s*$", re.IGNORECASE)
RE_ORG_TRUNC_START = re.compile(r"^РОССИИ\s+ПО\s", re.IGNORECASE)

def check_org_truncation(f):
    text = f["Issue_organization_ru"]["text"].strip().upper()
    if RE_ORG_TRUNC_END.search(text) or RE_ORG_TRUNC_START.match(text):
        return "org_truncated"
    return None

RE_BP_TRUNC_START = re.compile(r"^(Р-НА|РАЙОНА|Р-Н|РАЙОН)\s", re.IGNORECASE)

def check_bp_truncation(f):
    text = f["Birth_place_ru"]["text"].strip().upper()
    if RE_BP_TRUNC_START.match(text):
        return "bp_truncated"
    return None

def check_names(f):
    for k in ("Last_name_ru", "First_name_ru", "Middle_name_ru"):
        if not RE_NAME.match(f[k]["text"]):
            return f"name_chars_{k}"
    bp = f["Birth_place_ru"]["text"]
    if not bp or not re.search(r"[А-Яа-яЁё]", bp):
        return "birthplace_empty"
    org = f["Issue_organization_ru"]["text"]
    if not org or not RE_ORG.match(org):
        return "org_chars"
    return None


def add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)

def check_dates(f):
    issue = parse_date(f["Issue_date"]["text"])
    birth = parse_date(f["Birth_date"]["text"])
    if issue is None or birth is None: return "date_parse"
    if issue > REF_DATE:               return "issue_future"
    if birth > issue:                  return "birth_after_issue"
    if issue < add_years(REF_DATE, -45):  return "expired_45y"

    age = REF_DATE.year - birth.year - (
        (REF_DATE.month, REF_DATE.day) < (birth.month, birth.day)
    )
    if age < 14:                       return "too_young"
    if 20 <= age < 45:
        if issue < add_years(birth, 20):  return "issue_before_20"
    if age >= 45:
        if issue < add_years(birth, 45):  return "issue_before_45"
    return None

def check_subdivision(f, codes):
    if f["Issue_organisation_code"]["text"] not in codes:
        return "code_unknown"
    return None


NAME_FIELDS = {"Last_name_ru", "First_name_ru", "Middle_name_ru"}

def check_confidence(f, source):
    extra = TH["mobile_extra"] if source in ("mobile", "mobile_v2") else 0.0
    for name, v in f.items():
        if v is None:
            return f"missing_{name}"
        if v["conf"] < TH["conf"] + extra:
            return f"low_conf_{name}"
        if name in NAME_FIELDS:
            threshold = TH["char_conf_names"]
        elif name == "Issue_organization_ru":
            threshold = TH["char_conf_org"]
        else:
            threshold = TH["char_conf"]
        if v["min_char"] < threshold + extra:
            return f"low_char_{name}"
    return None

def check_quality(pred):
    q = pred.get("quality") or {}
    if TH["sharpness"] is not None and q.get("sharpness", 1) < TH["sharpness"]:
        return "low_sharpness"
    if TH["glare"] is not None and q.get("glare", 0) > TH["glare"]:
        return "high_glare"
    return None

# ------------------------- MRZ (TD3, 2x44) -------------------------
def _yy(s):
    y = int(s)
    return y + 1900 if y > 30 else y + 2000

def parse_mrz(pred):
    mrz = pred.get("mrz")
    if not mrz or not mrz.get("lines"): return None
    lines = [l["text"] for l in mrz["lines"]]
    if len(lines) < 2: return None
    l1, l2 = lines[0], lines[1]
    if not (l1.startswith("P") and len(l2) >= 28): return None
    out = {}
    try:
        if re.match(r"^\d{6}", l2[13:19]):
            yy, mm, dd = l2[13:15], l2[15:17], l2[17:19]
            out["Birth_date"] = f"{dd}.{mm}.{_yy(yy)}"
        if l2[20] in "MF":
            out["Sex_ru"] = "МУЖ." if l2[20] == "M" else "ЖЕН."
        if re.match(r"^\d{6}", l2[21:27]):
            yy, mm, dd = l2[21:23], l2[23:25], l2[25:27]
            out["Issue_date"] = f"{dd}.{mm}.{_yy(yy)}"
        num = re.sub(r"\D", "", l2[0:9])
        if num:
            out["_mrz_number"] = num
    except Exception:
        return None
    return out or None

def _norm(s):
    return " ".join(str(s or "").split()).upper()

def check_mrz(pred, f):
    m = parse_mrz(pred)
    if m is None:
        return None  # нет MRZ — не отклоняем только по этому признаку
    for k, v in m.items():
        if k == "_mrz_number":
            viz_num = re.sub(r"\D", "", f["Licence_number"]["text"])[-6:]
            if viz_num != v[-6:]:
                return "mrz_mismatch_number"
        elif k in f and f[k] and _norm(f[k]["text"]) != _norm(v):
            return f"mrz_mismatch_{k}"
    return None

# ------------------------- главная логика -------------------------
def check_strict(f):
    for name, v in f.items():
        if v is None:
            return f"strict_missing_{name}"
        if v["min_char"] < 0.94:
            return f"strict_low_char_{name}"
        if v["conf"] < 0.99:
            return f"strict_low_conf_{name}"
    return None

def decide(pred, codes):
    if not (pred.get("viz") or {}):
        return "reject", "empty_viz", {}

    f = extract_fields(pred)
    if any(v is None for v in f.values()):
        return "reject", "missing_field", {}

    checks = [
    ("formats",     lambda: check_formats(f)),
    ("names",       lambda: check_names(f)),
    ("org_trunc",   lambda: check_org_truncation(f)),
    ("bp_trunc",    lambda: check_bp_truncation(f)),    
    ("dates",       lambda: check_dates(f)),
    ("subdivision", lambda: check_subdivision(f, codes)),
    ("quality",     lambda: check_quality(pred)),
    ("mrz",         lambda: check_mrz(pred, f)),
]
    for _, fn in checks:
        err = fn()
        if err:
            return "reject", err, {}

    err = check_confidence(f, pred.get("source", "web"))
    if err:
        return "reject", err, {}

    err = check_strict(f)          # ← ДОБАВИТЬ
    if err:                        # ← ДОБАВИТЬ
        return "reject", err, {}   # ← ДОБАВИТЬ

    return "accept", "ok", {k: v["text"] for k, v in f.items()}

# ------------------------- CLI -------------------------
def main(inp, outp):
    is_train = "train" in inp
    codes = load_subdivisions(
        train_labels="data/train_labels.jsonl" if is_train else None
    )
    with open(inp, encoding="utf-8") as fin, \
         open(outp, "w", encoding="utf-8") as fout:
        for line in fin:
            pred = json.loads(line)
            decision, reason, fields = decide(pred, codes)
            rec = {"doc_id": pred["doc_id"],
                   "decision": decision,
                   "fields": fields if decision == "accept" else {}}
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")