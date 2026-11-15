"""Shared helpers for the DS-311 labs (case: Bayyin Consumer Protection Office).

Loading the synthetic data, quick mode, checks and safety nets, the agreement and interval
functions later labs reuse, masking, and one chat-completions call with a cache and a stand-in.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

LABS = Path(__file__).resolve().parent
DATA = LABS / "data"
REF = DATA / "reference"
ART = LABS / "artifacts"
CACHE = LABS / "cache"
QUICK = os.environ.get("DS311_QUICK", "0") == "1"

CATS = ["REFUND", "DEFECT", "DELIVERY", "PRICE", "AD", "WARRANTY"]
VARIETIES = ["msa", "gulf", "english", "mixed"]
FACTS = ["asked_refund", "refund_refused", "faulty", "not_as_described", "within_warranty", "repair_refused",
         "late", "not_delivered", "charged_more", "advert_claim"]


def pick(full, quick):
    """The small value in quick mode (DS311_QUICK=1), the full one otherwise."""
    return quick if QUICK else full


def check(cond, msg: str) -> None:
    print(("✅ " if cond else "❌ ") + msg)


def reference(name: str):
    """A reference result for the safety-net cells (data/reference/<name>.json)."""
    return json.loads((REF / f"{name}.json").read_text(encoding="utf-8"))


def art(lab: str) -> Path:
    """A fresh output folder for one lab: labs/artifacts/<lab>/ (git ignores it)."""
    p = ART / lab
    p.mkdir(parents=True, exist_ok=True)
    return p


def read(rel: str, **kw) -> pd.DataFrame:
    """Read a CSV (optionally .gz) under labs/data/ with every column as text unless told otherwise."""
    kw.setdefault("dtype", str)
    kw.setdefault("keep_default_na", False)
    return pd.read_csv(DATA / rel, **kw)


def expert_labels(ids) -> pd.Series:
    """The expert panel's label for each complaint id (Khulood Bin Saedan's adjudicated reading).
    In the case this is what labelling a golden set by experts returns; it costs the office time."""
    t = read("reference/truth_labels.csv.gz", usecols=["complaint_id", "category"]).set_index("complaint_id").category
    return t.reindex(list(ids))


# ---------------------------------------------------------------- guideline v1.1 (reference)
def apply_rules(f: dict) -> str:
    """Decision rules of guideline v1.1, in order. `f` holds the facts read from one complaint (0 or 1)."""
    g = lambda k: int(f.get(k, 0) or 0)
    if g("within_warranty") and g("repair_refused"):
        return "WARRANTY"
    if g("asked_refund") and g("refund_refused"):
        return "REFUND"
    if g("faulty") or g("not_as_described"):
        return "DEFECT"
    if g("late") or g("not_delivered"):
        return "DELIVERY"
    if g("charged_more"):
        return "PRICE"
    if g("advert_claim"):
        return "AD"
    return "OTHER"


# ---------------------------------------------------------------- agreement
def cohen_kappa(a, b) -> float:
    a, b = list(a), list(b)
    n = len(a)
    cats = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def krippendorff_alpha(units) -> float:
    """Nominal alpha. `units` is a list of lists of labels per item; None or '' is a missing label."""
    from collections import Counter
    coinc = Counter()
    for u in units:
        vals = [v for v in u if v not in (None, "")]
        m = len(vals)
        if m < 2:
            continue
        for i, x in enumerate(vals):
            for j, y in enumerate(vals):
                if i != j:
                    coinc[(x, y)] += 1 / (m - 1)
    n_c = Counter()
    for (x, _), w in coinc.items():
        n_c[x] += w
    n = sum(n_c.values())
    if n <= 1:
        return float("nan")
    do = sum(w for (x, y), w in coinc.items() if x != y) / n
    de = sum(n_c[x] * n_c[y] for x in n_c for y in n_c if x != y) / (n * (n - 1))
    return 1.0 if de == 0 else 1 - do / de


def bootstrap(fn, units, reps: int = 1000, seed: int = 311, level: float = 0.95):
    """Percentile interval of fn(units) over items resampled with replacement."""
    rng = random.Random(seed)
    n = len(units)
    vals = sorted(fn([units[rng.randrange(n)] for _ in range(n)]) for _ in range(reps))
    lo = vals[int((1 - level) / 2 * reps)]
    hi = vals[min(reps - 1, int((1 + level) / 2 * reps))]
    return round(lo, 3), round(hi, 3)


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    # Unrounded on purpose: a pass rule compares the bound itself, and 0.7998 rounds to 0.800.
    return c - h, c + h


# ---------------------------------------------------------------- personal data
TO_LATIN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
PII_PATTERNS = {
    "IBAN": r"\bSA\d{22}\b",
    "EMAIL": r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
    "PHONE": r"(?<!\d)05\d{8}(?!\d)",
    "NATIONAL_ID": r"(?<!\d)[12]\d{9}(?!\d)",
}


def residual_digits(text: str) -> bool:
    """True when a run of seven or more digits (Latin or Arabic-Indic) is left: treat the text as Restricted."""
    return re.search(r"\d{7,}", text.translate(TO_LATIN)) is not None


# ---------------------------------------------------------------- one model call, cached, with a stand-in
MODEL = os.environ.get("BAYYIN_MODEL", "google/gemma-4-31b-it:free")
FALLBACKS = [m for m in os.environ.get("BAYYIN_FALLBACKS", "google/gemma-4-26b-a4b-it:free").split(",") if m]
BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LAST_SOURCE = {"source": ""}

KEYWORDS = {
    "WARRANTY": ["warranty", "ضمان"],
    "REFUND": ["refund", "money back", "استرداد", "فلوسي", "نرجع فلوس", "إعادة المبلغ"],
    "PRICE": ["charged", "invoice", "shelf", "حاسبوني", "الفاتورة", "بالفاتورة", "على الرف", "لكن دفعت"],
    "AD": ["advert", "offer", " ad ", "الإعلان", "العرض"],
    "DELIVERY": ["deliver", "arrive", "التوصيل", "يصل", "ما وصل", "لم يصل", "استلم"],
    "DEFECT": ["broken", "fault", "stopped", "not the model", "different", "defect", "damaged", "مكسور", "عيب", "خرب", "خراب", "توقف", "مو نفس", "ليس الطراز", "يختلفان"],
}


def _key() -> str:
    for name in ("OPENROUTER_API_KEY", "LLM_API_KEY"):
        if os.environ.get(name):
            return os.environ[name]
    env = LABS / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    try:  # Colab secrets
        from google.colab import userdata  # type: ignore
        return userdata.get("OPENROUTER_API_KEY") or ""
    except Exception:
        return ""


def stand_in(messages) -> str:
    """A scripted stand-in for the model: keyword rules, used when no key works. Its answers are not a model's."""
    text = " " + messages[-1]["content"].lower() + " "
    for cat in ["WARRANTY", "REFUND", "PRICE", "AD", "DELIVERY", "DEFECT"]:
        if any(k.lower() in text for k in KEYWORDS[cat]):
            return cat
    return "DEFECT"


def chat(messages, model: str | None = None, temperature: float = 0.0, max_tokens: int = 20) -> str:
    """One chat-completions call. Replays identical requests from labs/cache/. Falls back to the stand-in
    when there is no key or the endpoint refuses; LAST_SOURCE says which answered."""
    model = model or MODEL
    body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    h = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]
    CACHE.mkdir(exist_ok=True)
    cf = CACHE / f"{h}.json"
    if cf.exists():
        LAST_SOURCE["source"] = "cache"
        return json.loads(cf.read_text(encoding="utf-8"))["content"]
    key = _key()
    if key:
        for m in [model] + FALLBACKS:
            req = urllib.request.Request(f"{BASE_URL}/chat/completions", data=json.dumps(dict(body, model=m)).encode(),
                                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    content = json.loads(r.read())["choices"][0]["message"]["content"] or ""
                cf.write_text(json.dumps({"model": m, "content": content}, ensure_ascii=False), encoding="utf-8")
                LAST_SOURCE["source"] = m
                return content
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError) as e:
                LAST_SOURCE["source"] = f"error {getattr(e, 'code', e)}"
                if getattr(e, "code", None) in (401, 403):
                    break
    LAST_SOURCE["source"] = "stand-in"
    return stand_in(messages)
