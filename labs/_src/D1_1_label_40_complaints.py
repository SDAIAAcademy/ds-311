# %% [markdown]
# # Lab 1.1 · Label 40 complaints, then compare
#
# Day 1 · Session 1 (What a label measures) · 25 min · **AI-off**: no assistant in this lab.
#
# Bayyin's analysts want complaints sorted into six categories. Before anyone writes a guideline, you
# label 40 complaints with only the category names, then compare with two neighbours. The point is
# not to be right: it is to see where three careful people measure different things.
#
# **Reference state.** `data/pilot/my40.csv` (40 complaints with an empty `label` column) and two
# neighbours' files, `data/pilot/neighbour_a.csv` and `neighbour_b.csv`. Swap files with the people
# beside you if you can; otherwise the supplied files stand in for them.
#
# **Tasks**
# - [ ] 1 · Label 40 complaints with only the six category names (12')
# - [ ] 2 · Load two neighbours' labels (3')
# - [ ] 3 · Percent agreement and the pairs that split you (5')
# - [ ] 4 · Three disagreements: what each of you measured (5')
# - [ ] ✱ Stretch · Agreement by language variety: Arabic, Gulf dialect, English, mixed

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

import pandas as pd
import bayyin as B

pd.set_option("display.max_colwidth", 120)
mine = B.read("pilot/my40.csv")
print(len(mine), "complaints;", mine.variety.value_counts().to_dict())
print("categories:", B.CATS)

# %% [markdown]
# ## 1 · Label 40 complaints (12')
#
# The six categories, and nothing more: **REFUND** refund refused · **DEFECT** defective or not as
# described · **DELIVERY** late or missing delivery · **PRICE** charged more than the displayed price ·
# **AD** misleading advert or offer · **WARRANTY** warranty or repair refused.
#
# ✏️ **Exercise** · Read each complaint and write one category in `MY_LABELS`, in the order of the
# file. Do not look anything up and do not ask an assistant. When you hesitate, write down why in
# `DOUBTS` (complaint id and a few words): you will need it in task 4.

# %%
for i, r in mine.iterrows():
    print(f"{i:2d} {r.complaint_id} [{r.variety}] {r.text}")

# %%
DOUBTS = {}
try:
    # BEGIN SOLUTION
    # The solution stands in for a participant with the labels of one example colleague.
    MY_LABELS = B.read("pilot/example_me.csv").label.tolist()
    DOUBTS = {"first doubt": "broken and refund refused: is it the defect or the refusal?"}
    # END SOLUTION
except NotImplementedError:
    # Safety net: an unfinished list is filled from the example colleague's labels
    MY_LABELS = B.read("pilot/example_me.csv").label.tolist()
    print("using the example colleague's labels")

# %%
assert len(MY_LABELS) == 40 and set(MY_LABELS) <= set(B.CATS), "40 labels, each one of the six categories"
mine["label"] = MY_LABELS
mine.to_csv(B.art("d1_1") / "my_labels.csv", index=False)
print(mine.label.value_counts().to_dict())

# %% [markdown]
# ## 2 · Load two neighbours' labels (3')
#
# Put your neighbours' files (same columns: `complaint_id,label`) in `artifacts/d1_1/` as
# `neighbour_a.csv` and `neighbour_b.csv`, or use the supplied ones.

# %%
def load_neighbour(name: str) -> pd.Series:
    own = B.ART / "d1_1" / f"{name}.csv"
    df = pd.read_csv(own, dtype=str) if own.exists() else B.read(f"pilot/{name}.csv")
    return df.set_index("complaint_id").label


table = mine[["complaint_id", "variety", "label"]].rename(columns={"label": "me"}).set_index("complaint_id")
table["a"] = load_neighbour("neighbour_a")
table["b"] = load_neighbour("neighbour_b")
B.check(table[["a", "b"]].notna().all().all(), "both neighbours labelled all 40")
table.head()

# %% [markdown]
# ## 3 · Percent agreement and the pairs that split you (5')
#
# ✏️ **Exercise** · Write `percent_agreement(x, y)`, the share of complaints two people labelled the
# same, and `split_pairs(table)`, a count of each unordered category pair that two of you gave the
# same complaint (for example `DEFECT|REFUND`), over all three pairs of people.

# %%
from collections import Counter


def percent_agreement(x, y) -> float:
    # BEGIN SOLUTION
    x, y = list(x), list(y)
    return sum(p == q for p, q in zip(x, y)) / len(x)
    # END SOLUTION


def split_pairs(t: pd.DataFrame) -> Counter:
    # BEGIN SOLUTION
    c = Counter()
    for _, r in t.iterrows():
        for p, q in (("me", "a"), ("me", "b"), ("a", "b")):
            if r[p] != r[q]:
                c["|".join(sorted([r[p], r[q]]))] += 1
    return c
    # END SOLUTION


# %%
try:
    pa = {f"{p}-{q}": round(percent_agreement(table[p], table[q]), 2) for p, q in (("me", "a"), ("me", "b"), ("a", "b"))}
    pairs = split_pairs(table)
except NotImplementedError:
    pa, pairs = {"me-a": 0.6, "me-b": 0.6, "a-b": 0.6}, Counter({"DEFECT|REFUND": 1})
all_three = (table.me == table.a) & (table.a == table.b)
print("percent agreement:", pa, "| all three agree on", int(all_three.sum()), "of 40")
print("pairs that split you:", pairs.most_common(5))
B.check(0 <= min(pa.values()) <= 1 and sum(pairs.values()) > 0, "agreement computed and splits counted")

# %% [markdown]
# 🔍 **Look at** the top pair. Is it two categories that are hard to tell apart in the text, or two
# questions you answered differently ("what went wrong" against "what the merchant refused")?

# %% [markdown]
# ## 4 · Three disagreements: what each of you measured (5')
#
# ✏️ **Exercise** · Pick three complaints where all three of you differ or two of you differ on the
# top pair. For each, write in `EXPLAIN` the question each label answered. These become the first
# edge cases of the guideline in Lab 1.2.

# %%
split = table[~all_three].join(mine.set_index("complaint_id").text)
print(split.head(8).to_string())
EXPLAIN = {}
try:
    # BEGIN SOLUTION
    for cid in split.index[:3]:
        r = split.loc[cid]
        EXPLAIN[cid] = f"me={r.me}, a={r.a}, b={r.b}: one label names the product's fault, another the merchant's refusal"
    # END SOLUTION
except NotImplementedError:
    EXPLAIN = {cid: "not written yet" for cid in split.index[:3]}
B.check(len(EXPLAIN) >= 3, "three disagreements explained")
_ = (B.art("d1_1") / "disagreements.txt").write_text("\n".join(f"{k}: {v}" for k, v in EXPLAIN.items()), encoding="utf-8")

# %% [markdown]
# ## ✱ Stretch · Agreement by language variety
#
# Compute the share where all three agree for each `variety`. Twelve or fewer complaints per group
# give a rough number: say how rough before you draw a conclusion.

# %%
try:
    # BEGIN SOLUTION
    by_var = table.assign(all3=all_three).groupby("variety").all3.agg(["mean", "size"]).round(2)
    print(by_var)
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Two of you agree on 30 of 40 complaints. Why is 75% not yet a measure of quality?
#    <details><summary>Answer</summary>Some agreement happens by chance, more so when one category is common; and agreeing can still mean agreeing on the wrong construct. Session 3 corrects for chance.</details>
# 2. Your top split is DEFECT against REFUND. What question does each label answer?
#    <details><summary>Answer</summary>DEFECT answers "what is wrong with the product"; REFUND answers "what did the merchant refuse". A guideline must say which question the label measures.</details>
# 3. Why is this lab done without an assistant?
#    <details><summary>Answer</summary>The disagreements you produce on your own are the evidence the guideline is written from; an assistant's labels would hide them.</details>
#
# **Carry forward.** `artifacts/d1_1/disagreements.txt` feeds the edge cases of Lab 1.2; the lab
# itself starts from the supplied edge cases if this file is missing.
