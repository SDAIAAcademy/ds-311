# %% [markdown]
# # Lab 3.3 · Merchant names across two scripts
#
# Day 3 · Session 3 (Duplicates and merchant matching) · 25 min · AI-tutor.
#
# One complaint in five arrives without a merchant id: only the name the complainant typed, in
# Arabic, in Latin letters, or a mix ("Alnoor Elec.", «مؤسسة النور للإلكترونيات المحدودة»). Hatoon's
# per-merchant figures need the registry id. You normalise both scripts, compare names through a
# transliteration key, choose a threshold, and measure precision first: a wrong match blames the
# wrong merchant.
#
# **Reference state.** `data/sources_clean/merchants.csv` (150 merchants, Arabic and English names),
# `data/matching/merchant_raw.csv` (600 raw names) and `data/matching/labelled_300.csv` (300 of them
# with the right merchant id, or `NONE` for a merchant not in the registry).
#
# **Tasks**
# - [ ] 1 · Normalise Arabic and Latin names (7')
# - [ ] 2 · A transliteration key across scripts (6')
# - [ ] 3 · Score, and choose a threshold (6')
# - [ ] 4 · Precision and recall on 300 labelled names (6')
# - [ ] ✱ Stretch · Blocking: compare fewer pairs

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/ds-311.git"
    if not Path("/content/ds-311").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/ds-311"], check=True)
    os.chdir("/content/ds-311/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("_tools").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

import re
import pandas as pd
from rapidfuzz import fuzz
import bayyin as B

reg = B.read("sources_clean/merchants.csv")
raw = B.read("matching/merchant_raw.csv")
lab = B.read("matching/labelled_300.csv")
print(len(reg), "registry merchants;", len(raw), "raw names;", len(lab), "labelled")
print(raw.name_raw.sample(8, random_state=1).tolist())

# %% [markdown]
# ## 1 · Normalise Arabic and Latin names (7')
#
# Supplied: Arabic letters with several written forms are unified (`UNIFY`); the words that carry no
# identity (`FILLER`: legal forms, "home", "parts"); and for each of the six registry sectors the stems
# that announce it in either script (`STEMS`). Stems, not whole words, because people write
# «لإلكترونيات», «للإلكترونيات», "Elec." and even glue the sector to the name («الفارسللأزياء»).
#
# ✏️ **Exercise** · Write `normalise(name)`: lower case, diacritics removed, Arabic forms unified,
# punctuation to spaces; a word holding a sector stem sets the sector and is dropped (keep any name
# glued before it); filler dropped; the article (`ال`, `al`) removed from the start of each name word.
# Return `(name_words, sector)`.

# %%
UNIFY = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ؤ": "و", "ئ": "ي", "ى": "ي", "ة": "ه", "ـ": None})
DIACRITICS = re.compile("[\u064B-\u0652]")
FILLER = {"شركه", "موسسه", "متجر", "محدوده", "المحدوده", "co", "est", "llc", "ltd", "home", "parts",
          "قطع", "لقطع", "منزليه", "المنزليه", "al", "ال"}
STEMS = {"electronics": ["لكترون", "elec"], "appliances": ["اجهز", "appl"], "furniture": ["اثاث", "furn"],
         "fashion": ["ازياء", "fash"], "jewellery": ["مجوهر", "jewel"], "auto": ["غيار", "سيارات", "auto"]}


def normalise(name: str) -> tuple[list[str], str]:
    # BEGIN SOLUTION
    s = DIACRITICS.sub("", name.lower()).translate(UNIFY)
    s = re.sub(r"[^\w\s]|_", " ", s)
    words, sector = [], ""
    for w in s.split():
        hit = next(((sec, w.index(st)) for sec, sts in STEMS.items() for st in sts if st in w), None)
        if hit:
            sector = hit[0]
            glued = re.sub(r"(لل|ال|ل|لا)$", "", w[:hit[1]])  # name glued before the sector word
            if len(glued) >= 2:
                words.append(glued)
            continue
        if w not in FILLER:
            words.append(w)
    words = [w[2:] if w.startswith(("ال", "al")) and len(w) > 4 else w for w in words]
    return words, sector
    # END SOLUTION


for n in ["مؤسسة النور للإلكترونيات المحدودة", "AL-NOOR ELECTRONICS CO.", "Alnoor Elec.", "النور Electronics",
          "شركة الفارسللأزياء المحدودة"]:
    try:
        print(n, "->", normalise(n))
    except NotImplementedError:
        print("normalise() not written yet")
        break

# %% [markdown]
# ## 2 · A transliteration key across scripts (6')
#
# "Al-Noor" and «النور» share their consonants: n, r. The key keeps a name's consonant skeleton in Latin
# letters: Arabic letters through `AR2LAT`; Latin vowels dropped; weak letters (w, y in Latin; ا و ي ء ه
# at the end in Arabic) dropped except at the start of a word; double letters collapsed; a final "h"
# after a vowel dropped (Safwah, Najmah).
#
# ✏️ **Exercise** · Write `key(name)` returning `"<skeleton>|<sector>"`.

# %%
AR2LAT = {"ب": "b", "ت": "t", "ث": "th", "ج": "j", "ح": "h", "خ": "kh", "د": "d", "ذ": "dh", "ر": "r", "ز": "z",
          "س": "s", "ش": "sh", "ص": "s", "ض": "d", "ط": "t", "ظ": "z", "ع": "", "غ": "gh", "ف": "f", "ق": "q",
          "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w", "ي": "y", "ا": "", "ء": "", "ؤ": "", "ئ": ""}


def skeleton(word: str) -> str:
    # BEGIN SOLUTION
    if re.search(r"[؀-ۿ]", word):
        w = word[:-1] if word.endswith("ه") else word  # ta marbuta, unified to ه
        out = []
        for i, ch in enumerate(w):
            lat = AR2LAT.get(ch, "")
            if lat in ("w", "y") and i > 0:
                lat = ""
            out.append(lat)
        s = "".join(out)
    else:
        w = re.sub(r"(?<=[aeiou])h$", "", word)
        s = w[0] + re.sub(r"[aeiouwy]", "", w[1:]) if w[0] in "wy" else re.sub(r"[aeiouwy]", "", w)
    return re.sub(r"(.)\1+", r"\1", s)
    # END SOLUTION


def key(name: str) -> str:
    words, sector = normalise(name)
    return " ".join(skeleton(w) for w in words) + "|" + sector


try:
    for a, b in [("النور للإلكترونيات", "Al-Noor Electronics"), ("الصفوة للأثاث", "Al Safwah Furniture"),
                 ("الياسمين للمجوهرات", "Alyasmin Jewellery"), ("الوفاق للأزياء", "Al-Wifaq Fashion")]:
        print(f"{a} -> {key(a)}   {b} -> {key(b)}")
    B.check(key("النور للإلكترونيات") == key("Al-Noor Electronics"), "the two scripts give one key")
except NotImplementedError:
    print("key() not written yet")

# %% [markdown]
# ## 3 · Score, and choose a threshold (6')
#
# Each raw name is compared with the registry keys of its sector (the Arabic and the English name give
# the same key; keep both). When no sector was recognised (a misspelt "Fasion", or a sector the
# registry does not hold, like "Toys"), it is compared with every key. A score is `fuzz.ratio` between
# the name skeletons, from 0 to 100. The best candidate is kept with its score; the threshold is chosen
# in task 4. When two merchants tie for the best score, return `NONE`: the name does not say which.
#
# ✏️ **Exercise** · Write `best_match(raw_name)` returning `(merchant_id, score)`.

# %%
try:
    reg["key_ar"] = reg.name_ar.map(key)
    reg["key_en"] = reg.name_en.map(key)
    B.check((reg.key_ar == reg.key_en).mean() > 0.95, f"Arabic and English registry names agree on the key for {(reg.key_ar == reg.key_en).mean():.0%} of merchants")
    KEYS = pd.concat([reg[["merchant_id", "key_ar"]].rename(columns={"key_ar": "k"}),
                      reg[["merchant_id", "key_en"]].rename(columns={"key_en": "k"})]).drop_duplicates()
    print("keys shared by two merchants:", KEYS.groupby("k").merchant_id.nunique().gt(1).sum())
except NotImplementedError:
    KEYS = None


def best_match(name: str) -> tuple[str, float]:
    # BEGIN SOLUTION
    k = key(name)
    skel, sector = k.split("|")
    cands = KEYS[KEYS.k.str.endswith("|" + sector)] if sector else KEYS
    if not len(cands) or not skel:
        return "NONE", 0.0
    scores = cands.k.map(lambda c: fuzz.ratio(skel, c.split("|")[0]))
    best = cands.merchant_id[scores.values == scores.max()].unique()
    if len(best) > 1:  # a tie between merchants: do not guess
        return "NONE", float(scores.max())
    return best[0], float(scores.max())
    # END SOLUTION


try:
    m = lab.name_raw.map(best_match)
    lab["pred"], lab["score"] = [x[0] for x in m], [x[1] for x in m]
except (NotImplementedError, TypeError):
    ref = B.read("reference/d3_3_matches.csv", dtype={"score": float}).set_index("raw_id")
    lab["pred"], lab["score"] = lab.raw_id.map(ref.pred), lab.raw_id.map(ref.score)
print("a bare «النور» ->", best_match("النور") if KEYS is not None else "")
print(lab.sort_values("score").head(8)[["name_raw", "merchant_id", "pred", "score"]].to_string(index=False))

# %% [markdown]
# ## 4 · Precision and recall on 300 labelled names (6')
#
# Precision: of the matches made, the share that is right. Recall: of the names whose merchant is in
# the registry, the share matched to it.
#
# ✏️ **Exercise** · Compute both for thresholds from 30 to 100 and pick the lowest threshold whose
# precision is at least 0.98. A name matched to `NONE` is not a match made.

# %%
def pr(t: float) -> dict:
    # BEGIN SOLUTION
    made = (lab.score >= t) & (lab.pred != "NONE")
    right = made & (lab.pred == lab.merchant_id)
    in_reg = lab.merchant_id != "NONE"
    return dict(threshold=t, matched=int(made.sum()), precision=round(right.sum() / max(made.sum(), 1), 3),
                recall=round((right & in_reg).sum() / in_reg.sum(), 3))
    # END SOLUTION


try:
    curve = pd.DataFrame([pr(t) for t in range(30, 101, 5)])
except NotImplementedError:
    curve = pd.DataFrame(B.reference("d3_3_curve"))
print(curve.to_string(index=False))
ok = curve[curve.precision >= 0.98]
T = float(ok.threshold.min()) if len(ok) else 100.0
row = curve[curve.threshold == T].iloc[0]
print(f"threshold {T}: precision {row.precision}, recall {row.recall}")
B.check(row.precision >= 0.98 and row.recall >= 0.85, "precision of at least 0.98 with recall of at least 0.85")
out = B.art("d3_3")
lab.to_csv(out / "matches.csv", index=False)
curve.to_json(out / "curve.json", orient="records", indent=1)

# %% [markdown]
# 🔍 **Look at** the curve before the threshold. Precision stays high at every threshold because the
# key and the tie rule do most of the work; the threshold only decides the names whose sector word was
# misspelt and that fell back to all keys. Then look at the misses: which are typing errors in the
# sector, which in the name? A fix belongs in `STEMS`, not in a lower threshold.

# %%
made = (lab.score >= T) & (lab.pred != "NONE")
wrong = lab[made & (lab.pred != lab.merchant_id)]
missed = lab[~made & (lab.merchant_id != "NONE")]
print("wrong:\n", wrong[["name_raw", "merchant_id", "pred", "score"]].to_string(index=False))
print("missed:\n", missed.head(6)[["name_raw", "merchant_id", "pred", "score"]].to_string(index=False))

# %% [markdown]
# ## ✱ Stretch · Blocking
#
# Comparing every raw name with every registry key costs 600 × 300 comparisons. Compare only within a
# block: same sector and same first letter of the skeleton. How many comparisons remain, and does
# recall drop?

# %%
try:
    # BEGIN SOLUTION
    ks = raw.name_raw.map(key)
    blocks = ks.map(lambda k: (k.split("|")[1], k[:1]))
    reg_blocks = KEYS.k.map(lambda k: (k.split("|")[1], k[:1])).value_counts()
    print("comparisons with blocking:", int(blocks.map(reg_blocks).fillna(0).sum()), "of", len(raw) * len(KEYS))
    # END SOLUTION
except (NotImplementedError, TypeError, AttributeError):
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Why choose the threshold by precision first?
#    <details><summary>Answer</summary>A wrong match attributes a complaint to a merchant who did not cause it; a missed match leaves it unattributed, which analysts can see and handle.</details>
# 2. "Al-Ofuq" and "Al-Wifaq" would share a key if initial w were dropped. What does that tell you about keys?
#    <details><summary>Answer</summary>A key throws information away; check how many registry merchants share one, and keep enough (here the initial letter) to separate them.</details>
# 3. A complainant writes only "النور". Should it match?
#    <details><summary>Answer</summary>No: six merchants share that root; without the sector the right answer is NONE until someone checks.</details>
#
# **Carry forward.** `artifacts/d3_3/matches.csv`; the pipeline of Day 4 uses the registry id when the
# portal gives one.
