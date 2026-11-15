# %% [markdown]
# # Lab 2.2 · Gold checks and routing
#
# Day 2 · Session 2 (Gold questions and review queues) · 25 min · AI-tutor.
#
# Six raters, R1 to R6, labelled for ten days under guideline v1.1. Eight gold questions per rater
# per day were mixed into their work; a quarter of the items got a second, independent label; the
# few distressing complaints went only to the two raters approved for them. You score each rater on
# the gold questions with an interval, set a pass rule, and route every item: accept, adjudicate,
# re-label or the restricted queue.
#
# **Reference state.** `data/ops/ops_round.csv` (one row per label: day, rater, complaint, gold or
# not, distressing or not, label, seconds) and `data/ops/gold_bank.csv` (the gold answers).
#
# **Tasks**
# - [ ] 1 · Gold accuracy per rater, with an interval (6')
# - [ ] 2 · A pass rule with a minimum count (5')
# - [ ] 3 · Routing: accept, adjudicate, restricted queue (8')
# - [ ] 4 · Queue sizes and adjudicator hours (6')
# - [ ] ✱ Stretch · Gold questions a rater cannot spot

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

ops = B.read("ops/ops_round.csv", dtype={"day": int, "is_gold": int, "distressing": int, "seconds": int})
gold_bank = B.read("ops/gold_bank.csv").set_index("complaint_id").gold_label
print(len(ops), "labels;", ops.is_gold.sum(), "gold answers;", ops[ops.is_gold == 0].complaint_id.nunique(), "work items")
APPROVED_RESTRICTED = {"R2", "R4"}  # from guideline v1.1, wellbeing section

# %% [markdown]
# ## 1 · Gold accuracy per rater, with an interval (6')
#
# ✏️ **Exercise** · For each rater: the number of gold answers, the number right, the accuracy and a
# 95% Wilson interval (`B.wilson(k, n)`).

# %%
def gold_scores(ops: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    g = ops[ops.is_gold == 1].copy()
    g["right"] = g.label == g.complaint_id.map(gold_bank)
    s = g.groupby("rater").right.agg(n="size", k="sum")
    s["accuracy"] = (s.k / s.n).round(3)
    s[["lo", "hi"]] = [B.wilson(int(k), int(n)) for k, n in zip(s.k, s.n)]
    return s
    # END SOLUTION


try:
    scores = gold_scores(ops)
except NotImplementedError:
    scores = pd.DataFrame(B.reference("d2_2_routing")["scores"]).T
print(scores)
B.check(scores.loc["R6", "accuracy"] < 0.85 and scores.loc["R2", "accuracy"] > 0.9, "R6 scores lowest, R2 highest")

# %% [markdown]
# ## 2 · A pass rule with a minimum count (5')
#
# A rater who got 5 of 5 gold questions right has not shown 100% accuracy. The rule needs a
# minimum number of gold answers and judges the **lower** end of the interval.
#
# ✏️ **Exercise** · Write `status(row)`: `"too few"` below `MIN_GOLD` answers; `"pass"` when the
# lower bound is at least `LOWER`; `"watch"` otherwise.

# %%
MIN_GOLD, LOWER = 30, 0.80


def status(row) -> str:
    # BEGIN SOLUTION
    if row.n < MIN_GOLD:
        return "too few"
    return "pass" if row.lo >= LOWER else "watch"
    # END SOLUTION


try:
    scores["status"] = scores.apply(status, axis=1)
except NotImplementedError:
    scores["status"] = ["pass", "pass", "pass", "pass", "watch", "watch"]
print(scores[["n", "accuracy", "lo", "status"]])
watch = set(scores[scores.status != "pass"].index)
print("on watch:", sorted(watch))

# %% [markdown]
# 🔍 **Look at** R5: over ten days its accuracy looks acceptable or borderline. Lab 2.3 asks whether
# that average hides a change.

# %% [markdown]
# ## 3 · Routing: accept, adjudicate, restricted queue (8')
#
# Each work item (not gold) goes to exactly one place:
# - **restricted**: a distressing item, whatever its labels: only approved raters work this queue;
# - **adjudicate**: two labels that disagree;
# - **relabel**: one label only, from a rater on watch;
# - **accept**: everything else.
#
# ✏️ **Exercise** · Write `route(labels)` for the label rows of one item and return the queue name.

# %%
def route(rows: pd.DataFrame) -> str:
    # BEGIN SOLUTION
    if rows.distressing.max() == 1:
        return "restricted"
    if rows.label.nunique() > 1:
        return "adjudicate"
    if len(rows) == 1 and rows.rater.iloc[0] in watch:
        return "relabel"
    return "accept"
    # END SOLUTION


work = ops[ops.is_gold == 0]
try:
    queues = work.groupby("complaint_id").apply(route, include_groups=False)
except NotImplementedError:
    queues = pd.Series(B.reference("d2_2_routing")["queues"])
print(queues.value_counts())
B.check(set(queues.unique()) <= {"accept", "adjudicate", "relabel", "restricted"}, "every item has one queue")
restricted_ids = set(queues[queues == "restricted"].index)
breaches = work[work.complaint_id.isin(restricted_ids) & ~work.rater.isin(APPROVED_RESTRICTED)]
B.check(len(breaches) == 0, f"restricted items labelled only by approved raters ({len(breaches)} breaches)")

# %% [markdown]
# ## 4 · Queue sizes and adjudicator hours (6')
#
# The adjudicator (Khulood) takes about 90 seconds per item; a re-label takes the median time of the
# team. Turn the queues into hours of work for tomorrow.
#
# ✏️ **Exercise** · Compute `hours` per queue.

# %%
try:
    # BEGIN SOLUTION
    med = work.seconds.median()
    per_item = {"adjudicate": 90, "relabel": med, "restricted": 200, "accept": 0}
    hours = (queues.value_counts() * pd.Series(per_item) / 3600).round(2).dropna()
    # END SOLUTION
except NotImplementedError:
    hours = pd.Series(B.reference("d2_2_routing")["hours"])
print(hours)
pd.DataFrame({"items": queues.value_counts(), "hours": hours}).to_csv(B.art("d2_2") / "queues.csv")
(B.art("d2_2") / "routing.json").write_text(json.dumps({"scores": scores.drop(columns=["status"]).T.to_dict(),
                                                         "queues": queues.to_dict(), "hours": hours.to_dict()}, indent=1, default=float), encoding="utf-8")
B.check(hours.get("adjudicate", 0) > 0, "adjudication hours computed")

# %% [markdown]
# ## ✱ Stretch · Gold a rater cannot spot
#
# Compare the gold questions with ordinary work: variety mix and time spent. If gold items look
# different (all MSA, or answered much faster), raters learn to spot them.

# %%
try:
    # BEGIN SOLUTION
    print(ops.groupby("is_gold").variety.value_counts(normalize=True).unstack().round(2))
    print(ops.groupby("is_gold").seconds.median())
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. A new rater gets 9 of 9 gold questions right. Pass?
#    <details><summary>Answer</summary>Too few to say: the Wilson interval for 9 of 9 reaches down to about 0.70. Keep the rater on gold until the minimum count is reached.</details>
# 2. Why route a disagreement to adjudication rather than keep the label of the better rater?
#    <details><summary>Answer</summary>Gold accuracy is an average; on any single item the better rater can be the wrong one. Adjudication applies the guideline to that item.</details>
# 3. Why is the restricted queue decided before anything else?
#    <details><summary>Answer</summary>The wellbeing rule is a constraint, not a quality signal: a distressing item must reach an approved rater even when its label would otherwise be accepted.</details>
#
# **Carry forward.** `artifacts/d2_2/queues.csv` goes into the quality-control report; Lab 2.3 starts
# again from `data/ops/ops_round.csv`.
