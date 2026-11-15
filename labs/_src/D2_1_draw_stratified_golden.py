# %% [markdown]
# # Lab 2.1 · A stratified golden set
#
# Day 2 · Session 1 (Sampling a golden set) · 25 min · AI-tutor.
#
# Bayyin needs a golden set: complaints labelled by experts that are mixed into raters' work as
# gold questions. It must cover the rare category (WARRANTY) and the rare variety (mixed Arabic and
# English). You draw 240 complaints stratified on what is known **before** labelling (the language
# variety and a keyword pre-label), compare coverage with a simple random sample, and weight the
# stratified sample back to the population.
#
# **Reference state.** `data/corpus/corpus_index.csv.gz`: 30,000 complaint ids with `variety`,
# `channel` and `prelabel` (a keyword step, right about four times in five). Expert labels for any
# drawn complaint come from `B.expert_labels(ids)`.
#
# **Tasks**
# - [ ] 1 · What a random sample of 240 misses (4')
# - [ ] 2 · Strata from what is known before labelling (6')
# - [ ] 3 · Allocate with a floor per stratum, and draw (8')
# - [ ] 4 · Coverage under expert labels, and the weights (7')
# - [ ] ✱ Stretch · Keep half of the gold hidden for later audits

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

import json
import pandas as pd
import bayyin as B

idx = B.read("corpus/corpus_index.csv.gz")
N, n = len(idx), 240
print(N, "complaints;", idx.variety.value_counts().to_dict())
print("pre-labels:", idx.prelabel.value_counts().to_dict())

# %% [markdown]
# ## 1 · What a random sample of 240 misses (4')
#
# ✏️ **Exercise** · Draw a simple random sample of 240 (`random_state=311`), label it with the expert
# panel, and count how many WARRANTY complaints and how many mixed-variety complaints it holds.

# %%
def coverage(ids) -> dict:
    lab = B.expert_labels(ids)
    var = idx.set_index("complaint_id").variety.reindex(list(ids))
    return {"WARRANTY": int((lab == "WARRANTY").sum()), "mixed": int((var == "mixed").sum()),
            "WARRANTY in mixed": int(((lab == "WARRANTY") & (var == "mixed")).sum())}


try:
    # BEGIN SOLUTION
    srs = idx.sample(n, random_state=311)
    # END SOLUTION
except NotImplementedError:
    srs = idx.sample(n, random_state=311)
cov_srs = coverage(srs.complaint_id)
print("random sample:", cov_srs)

# %% [markdown]
# 🔍 Six or so WARRANTY items cannot tell you whether a rater gets WARRANTY right: a rater who misses
# all of them still scores above 95% on the gold set.

# %% [markdown]
# ## 2 · Strata from what is known before labelling (6')
#
# You cannot stratify on the true category: nobody knows it yet. You can stratify on fields known
# before labelling: the `variety` (from language detection) and the `prelabel`.
#
# ✏️ **Exercise** · Add a `stratum` column (`variety|prelabel`) and count the population size `N_h`
# of each stratum.

# %%
try:
    # BEGIN SOLUTION
    idx["stratum"] = idx.variety + "|" + idx.prelabel
    # END SOLUTION
except NotImplementedError:
    idx["stratum"] = idx.variety + "|" + idx.prelabel
N_h = idx.stratum.value_counts().sort_index()
print(len(N_h), "strata; smallest:", N_h.nsmallest(4).to_dict())

# %% [markdown]
# ## 3 · Allocate with a floor per stratum, and draw (8')
#
# Proportional allocation alone gives the smallest strata zero or one item. A floor gives every
# stratum at least `FLOOR` items (or all of it when smaller); the rest is shared in proportion to
# size.
#
# ✏️ **Exercise** · Write `allocate(N_h, n, floor)` returning integers that add up to `n`, then draw
# that many from each stratum (`random_state=311`).

# %%
FLOOR = 6


def allocate(N_h: pd.Series, n: int, floor: int) -> pd.Series:
    # BEGIN SOLUTION
    base = N_h.clip(upper=floor)
    rest = n - base.sum()
    room = N_h - base
    extra = (room / room.sum() * rest).round().astype(int)
    alloc = (base + extra).clip(upper=N_h)
    i = 0
    while alloc.sum() != n:  # fix rounding, largest strata first
        s = N_h.sort_values(ascending=False).index[i % len(N_h)]
        step = 1 if alloc.sum() < n else -1
        if alloc[s] + step <= N_h[s] and alloc[s] + step >= min(floor, N_h[s]):
            alloc[s] += step
        i += 1
    return alloc
    # END SOLUTION


try:
    n_h = allocate(N_h, n, FLOOR)
except NotImplementedError:
    n_h = pd.Series(B.reference("d2_1_coverage")["alloc"])
gold = pd.concat([idx[idx.stratum == s].sample(int(k), random_state=311) for s, k in n_h.items() if k > 0])
print("allocated", int(n_h.sum()), "| smallest allocations:", n_h.nsmallest(4).to_dict())
B.check(int(n_h.sum()) == n and (n_h >= N_h.clip(upper=FLOOR)).all(), "240 drawn, every stratum at its floor")

# %% [markdown]
# ## 4 · Coverage under expert labels, and the weights (7')
#
# Experts label the drawn complaints. Compare coverage with the random sample. Then weight: each
# drawn complaint stands for `N_h / n_h` complaints of its stratum. Weighted shares estimate the
# population; unweighted shares of an oversampled set do not.
#
# ✏️ **Exercise** · Compute the weighted and the unweighted category shares of the golden set.

# %%
gold["gold_label"] = B.expert_labels(gold.complaint_id).values
cov_gold = coverage(gold.complaint_id)
print("stratified:", cov_gold, "| random:", cov_srs)
gold["weight"] = gold.stratum.map(N_h / n_h)

try:
    # BEGIN SOLUTION
    unweighted = gold.gold_label.value_counts(normalize=True)
    weighted = gold.groupby("gold_label").weight.sum() / gold.weight.sum()
    # END SOLUTION
except NotImplementedError:
    unweighted = gold.gold_label.value_counts(normalize=True)
    weighted = gold.groupby("gold_label").weight.sum() / gold.weight.sum()
truth = B.expert_labels(idx.complaint_id).value_counts(normalize=True)
shares = pd.DataFrame({"unweighted": unweighted, "weighted": weighted, "whole corpus": truth}).round(3)
print(shares)
B.check(cov_gold["WARRANTY"] >= 2 * cov_srs["WARRANTY"] and cov_gold["mixed"] >= 2 * cov_srs["mixed"], "the stratified set at least doubles the rare category and the rare variety")
B.check(abs(shares.loc["WARRANTY", "weighted"] - shares.loc["WARRANTY", "whole corpus"]) < abs(shares.loc["WARRANTY", "unweighted"] - shares.loc["WARRANTY", "whole corpus"]), "weighting brings WARRANTY's share back toward the corpus")
out = B.art("d2_1")
gold[["complaint_id", "variety", "prelabel", "stratum", "gold_label", "weight"]].to_csv(out / "golden_set.csv", index=False)
(out / "coverage.json").write_text(json.dumps({"random": cov_srs, "stratified": cov_gold, "alloc": n_h.to_dict()}, indent=1), encoding="utf-8")

# %% [markdown]
# ## ✱ Stretch · A hidden half
#
# Raters who see the same gold questions every day learn them. Split the golden set in two halves,
# balanced by stratum: one half is used as gold questions now, the other is kept for audits nobody
# has seen.

# %%
try:
    # BEGIN SOLUTION
    gold["half"] = gold.groupby("stratum").cumcount() % 2
    print(gold.groupby("half").agg(n=("complaint_id", "size"), warranty=("gold_label", lambda s: int((s == "WARRANTY").sum()))))
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Why stratify on the pre-label and not on the true category?
#    <details><summary>Answer</summary>The true category is what labelling produces; before it, only fields such as variety and a pre-label exist. The pre-label is imperfect, which is why coverage is checked after experts label the sample.</details>
# 2. The golden set over-represents WARRANTY. When must you weight?
#    <details><summary>Answer</summary>Whenever the golden set estimates something about the population, such as category shares; not when it only scores raters item by item.</details>
# 3. What does a floor of six per stratum cost?
#    <details><summary>Answer</summary>Fewer items for the large strata, so their estimates are less precise; the trade is worth it when rare cases are what the gold questions must test.</details>
#
# **Carry forward.** `artifacts/d2_1/golden_set.csv`. The operations round of Labs 2.2 to 2.4 uses
# the office's own gold bank (`data/ops/gold_bank.csv`), so nothing later depends on this file.
