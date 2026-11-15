# %% [markdown]
# # Lab 1.3 · Kappa and alpha on the pilot
#
# Day 1 · Session 3 (Agreement statistics) · 25 min · AI-tutor.
#
# Three raters, R1 to R3, labelled the same 300 complaints in the first pilot round with only the
# category names. You measure how far they agree beyond chance: percent agreement, Cohen's kappa for
# each pair, Krippendorff's alpha from the coincidence matrix, then by category and language variety
# with bootstrap intervals. This is the agreement report the guideline's revision will cite.
#
# **Reference state.** `data/pilot/pilot_round1.csv` (300 complaints, three labels each).
#
# **Tasks**
# - [ ] 1 · Percent agreement, and why it flatters (4')
# - [ ] 2 · Cohen's kappa for each pair of raters (6')
# - [ ] 3 · Krippendorff's alpha from the coincidence matrix (7')
# - [ ] 4 · By category and by variety, with intervals (8')
# - [ ] ✱ Stretch · Alpha when one rater skipped twenty complaints

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
from collections import Counter
from itertools import combinations

import pandas as pd
import bayyin as B

r1 = B.read("pilot/pilot_round1.csv")
RATERS = ["R1", "R2", "R3"]
units = r1[RATERS].values.tolist()
print(len(units), "complaints; label counts:", Counter(x for u in units for x in u).most_common())

# %% [markdown]
# ## 1 · Percent agreement, and why it flatters (4')
#
# ✏️ **Exercise** · Compute the share of complaints where all three agree, and the mean pairwise
# agreement. Then compute the pairwise agreement two raters would reach **by chance** if each kept
# their own label frequencies but labelled at random: the sum over categories of p_a(c) × p_b(c).

# %%
def all_agree(units) -> float:
    # BEGIN SOLUTION
    return sum(len(set(u)) == 1 for u in units) / len(units)
    # END SOLUTION


def chance_agreement(a, b) -> float:
    # BEGIN SOLUTION
    a, b = list(a), list(b)
    n = len(a)
    return sum((a.count(c) / n) * (b.count(c) / n) for c in set(a) | set(b))
    # END SOLUTION


# %%
try:
    pa_all = all_agree(units)
    pair_pa = {f"{x}-{y}": float((r1[x] == r1[y]).mean()) for x, y in combinations(RATERS, 2)}
    pair_pe = {f"{x}-{y}": chance_agreement(r1[x], r1[y]) for x, y in combinations(RATERS, 2)}
except NotImplementedError:
    ref = B.reference("d1_3_agreement")
    pa_all, pair_pa, pair_pe = ref["all_agree"], ref["pair_pa"], ref["pair_pe"]
print("all three agree:", round(pa_all, 3))
print("pairwise:", {k: round(v, 3) for k, v in pair_pa.items()})
print("by chance:", {k: round(v, 3) for k, v in pair_pe.items()})
B.check(0.45 < pa_all < 0.65, "all-three agreement is about half")

# %% [markdown]
# ## 2 · Cohen's kappa for each pair of raters (6')
#
# kappa = (p_o − p_e) / (1 − p_e): the share of the agreement **above chance** that the raters reached.
#
# ✏️ **Exercise** · Write `kappa(a, b)` from the two functions above. The check compares it with
# scikit-learn-free reference code in `bayyin.cohen_kappa`.

# %%
def kappa(a, b) -> float:
    # BEGIN SOLUTION
    a, b = list(a), list(b)
    po = sum(x == y for x, y in zip(a, b)) / len(a)
    pe = chance_agreement(a, b)
    return (po - pe) / (1 - pe)
    # END SOLUTION


try:
    kappas = {f"{x}-{y}": round(kappa(r1[x], r1[y]), 3) for x, y in combinations(RATERS, 2)}
except NotImplementedError:
    kappas = {f"{x}-{y}": round(B.cohen_kappa(r1[x], r1[y]), 3) for x, y in combinations(RATERS, 2)}
print("kappa by pair:", kappas)
B.check(all(abs(kappas[f"{x}-{y}"] - B.cohen_kappa(r1[x], r1[y])) < 1e-3 for x, y in combinations(RATERS, 2)), "kappa matches the reference")

# %% [markdown]
# ## 3 · Krippendorff's alpha from the coincidence matrix (7')
#
# Alpha works for any number of raters and for missing labels. Each complaint with m labels adds,
# for every ordered pair of its labels (i ≠ j), 1/(m − 1) to cell (label_i, label_j) of the
# **coincidence matrix**. Then alpha = 1 − D_o / D_e, where D_o is the off-diagonal share of the
# matrix and D_e = Σ_{c≠k} n_c n_k / (n (n − 1)) from the row totals n_c.
#
# ✏️ **Exercise** · Build the matrix as a DataFrame and compute alpha.

# %%
def coincidence(units) -> pd.DataFrame:
    # BEGIN SOLUTION
    m = pd.DataFrame(0.0, index=B.CATS, columns=B.CATS)
    for u in units:
        vals = [v for v in u if v not in (None, "")]
        if len(vals) < 2:
            continue
        for i, x in enumerate(vals):
            for j, y in enumerate(vals):
                if i != j:
                    m.loc[x, y] += 1 / (len(vals) - 1)
    return m
    # END SOLUTION


def alpha(units) -> float:
    # BEGIN SOLUTION
    m = coincidence(units)
    n_c = m.sum(axis=1)
    n = n_c.sum()
    d_o = (m.values.sum() - m.values.trace()) / n
    d_e = (n_c.sum() ** 2 - (n_c ** 2).sum()) / (n * (n - 1))
    return 1 - d_o / d_e
    # END SOLUTION


try:
    print(coincidence(units).round(1))
    a_all = alpha(units)
except NotImplementedError:
    a_all = B.krippendorff_alpha(units)
print("alpha, round 1:", round(a_all, 3))
B.check(abs(a_all - B.krippendorff_alpha(units)) < 1e-9, "alpha matches the reference")

# %% [markdown]
# 🔍 **Look at** the off-diagonal cells of the matrix: the largest ones are the category pairs the
# guideline must separate. Compare them with your own splits from Lab 1.1.

# %% [markdown]
# ## 4 · By category and by variety, with intervals (8')
#
# By category: alpha on a yes/no question ("is it this category?") for each code. By variety: alpha on
# the subset of complaints. Each with a 95% bootstrap interval over complaints
# (`B.bootstrap(fn, units, reps)`; quick mode uses fewer resamples).
#
# ✏️ **Exercise** · Fill `report`: one row per category and per variety with `n`, `alpha`, `lo`, `hi`.

# %%
REPS = B.pick(1000, 200)
rows = []
try:
    # BEGIN SOLUTION
    for c in B.CATS:
        u = [[int(x == c) for x in row] for row in units]
        lo, hi = B.bootstrap(B.krippendorff_alpha, u, REPS)
        rows.append(dict(group="category", name=c, n=sum(row.count(c) for row in units), alpha=round(B.krippendorff_alpha(u), 3), lo=lo, hi=hi))
    for v in B.VARIETIES:
        u = r1[r1.variety == v][RATERS].values.tolist()
        lo, hi = B.bootstrap(B.krippendorff_alpha, u, REPS)
        rows.append(dict(group="variety", name=v, n=len(u), alpha=round(B.krippendorff_alpha(u), 3), lo=lo, hi=hi))
    # END SOLUTION
except NotImplementedError:
    rows = B.reference("d1_3_agreement")["report"]
report = pd.DataFrame(rows)
print(report.to_string(index=False))
worst = report[report.group == "category"].sort_values("alpha").iloc[0]
B.check(worst["name"] == "WARRANTY", "the weakest category is WARRANTY")
out = B.art("d1_3")
report.to_csv(out / "agreement_round1.csv", index=False)
(out / "agreement_round1.json").write_text(json.dumps(dict(all_agree=pa_all, pair_pa=pair_pa, pair_pe=pair_pe, kappas=kappas,
                                                         alpha=a_all, report=rows), indent=1), encoding="utf-8")

# %% [markdown]
# 🔍 **Look at** WARRANTY: how many labels carry it, and how wide is its interval? Then look at R3's
# column for the complaints the other two called WARRANTY.

# %%
w = r1[(r1.R1 == "WARRANTY") & (r1.R2 == "WARRANTY")]
print(len(w), "complaints both R1 and R2 called WARRANTY; R3 said:", w.R3.value_counts().to_dict())

# %% [markdown]
# ## ✱ Stretch · Alpha with missing labels
#
# Blank R2's label on twenty complaints (as if R2 skipped them) and recompute alpha. Kappa needs both
# labels of a pair; alpha uses whatever labels each complaint has.

# %%
try:
    # BEGIN SOLUTION
    skipped = [list(u) for u in units]
    for u in skipped[:20]:
        u[1] = ""
    print("alpha with twenty skipped:", round(B.krippendorff_alpha(skipped), 3))
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Two raters agree on 90% of complaints about a category that 90% of complaints belong to. What is kappa likely to be, and why?
#    <details><summary>Answer</summary>Near zero: chance agreement is already about 0.82 when both say the common category almost always, so little agreement is left above chance.</details>
# 2. Why report alpha by language variety and not only overall?
#    <details><summary>Answer</summary>An overall figure can hide a variety where the labels are unreliable; the analysis that uses the labels inherits that weakness for those complainants.</details>
# 3. Why does WARRANTY's interval come out so wide?
#    <details><summary>Answer</summary>Few complaints carry it, so a few disagreements move the estimate a lot; a rare category needs more items before its agreement can be trusted.</details>
#
# **Carry forward.** `artifacts/d1_3/agreement_round1.json` is compared with round 2 in Lab 1.4,
# which reads the reference copy when this file is missing.
