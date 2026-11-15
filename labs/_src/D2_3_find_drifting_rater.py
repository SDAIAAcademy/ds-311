# %% [markdown]
# # Lab 2.3 · Find the drifting rater
#
# Day 2 · Session 3 (Rater drift and workload) · 25 min · AI-tutor.
#
# Two raters ended Lab 2.2 on watch. One has always been weaker; the other was fine and then
# changed. They need different responses (coaching against retraining and re-checking recent work),
# so you must tell them apart. You track gold accuracy per rater over ten days, flag drift against
# each rater's own baseline, and check workload and distressing-content minutes against the
# guideline's limit.
#
# **Reference state.** `data/ops/ops_round.csv` and `data/ops/gold_bank.csv`.
#
# **Tasks**
# - [ ] 1 · Gold accuracy by rater and day (5')
# - [ ] 2 · A drift rule against each rater's own baseline (8')
# - [ ] 3 · Drift or steadily low? (5')
# - [ ] 4 · Workload and distressing-content minutes (7')
# - [ ] ✱ Stretch · Which categories does the drifting rater now confuse?

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
import math
import pandas as pd
import bayyin as B

ops = B.read("ops/ops_round.csv", dtype={"day": int, "is_gold": int, "distressing": int, "seconds": int})
gold_bank = B.read("ops/gold_bank.csv").set_index("complaint_id").gold_label
g = ops[ops.is_gold == 1].copy()
g["right"] = (g.label == g.complaint_id.map(gold_bank)).astype(int)
print(len(g), "gold answers over", g.day.nunique(), "days")

# %% [markdown]
# ## 1 · Gold accuracy by rater and day (5')
#
# ✏️ **Exercise** · A table with one row per rater, one column per day, the share of gold questions
# right (eight a day, so each cell is coarse).

# %%
try:
    # BEGIN SOLUTION
    daily = g.pivot_table(index="rater", columns="day", values="right", aggfunc="mean").round(2)
    # END SOLUTION
except NotImplementedError:
    daily = g.pivot_table(index="rater", columns="day", values="right", aggfunc="mean").round(2)
print(daily.to_string())

# %% [markdown]
# ## 2 · A drift rule against each rater's own baseline (8')
#
# Compare each rater's last three days with their own first five, with a one-sided two-proportion
# test: z = (p_base − p_recent) / sqrt(p (1 − p) (1/n_base + 1/n_recent)), p the pooled rate. Flag
# when the drop is at least 0.10 **and** z ≥ 2.
#
# ✏️ **Exercise** · Write `drift(rater_rows)` returning `p_base`, `p_recent`, `z` and `flag`.

# %%
BASE_DAYS, RECENT_DAYS = range(1, 6), range(8, 11)


def drift(rows: pd.DataFrame) -> pd.Series:
    # BEGIN SOLUTION
    b = rows[rows.day.isin(BASE_DAYS)].right
    r = rows[rows.day.isin(RECENT_DAYS)].right
    p = (b.sum() + r.sum()) / (len(b) + len(r))
    se = math.sqrt(p * (1 - p) * (1 / len(b) + 1 / len(r))) if 0 < p < 1 else float("inf")
    z = (b.mean() - r.mean()) / se
    return pd.Series({"p_base": round(b.mean(), 3), "p_recent": round(r.mean(), 3), "z": round(z, 2),
                      "flag": bool(b.mean() - r.mean() >= 0.10 and z >= 2)})
    # END SOLUTION


try:
    d = g.groupby("rater").apply(drift, include_groups=False)
except NotImplementedError:
    d = pd.DataFrame(B.reference("d2_3_drift")["drift"]).T
print(d)
B.check(list(d[d.flag.astype(bool)].index) == ["R5"], "only R5 is flagged for drift")

# %% [markdown]
# ## 3 · Drift or steadily low? (5')
#
# A team-average rule ("flag anyone more than 0.10 below the team's accuracy over all ten days")
# looks reasonable. Apply it and compare with your drift rule.
#
# ✏️ **Exercise** · Compute `team_flag` per rater and a one-word `diagnosis` per rater: `drift`,
# `steady-low` or `ok`.

# %%
try:
    # BEGIN SOLUTION
    overall = g.groupby("rater").right.mean()
    team_flag = overall < overall.mean() - 0.10
    diagnosis = pd.Series("ok", index=overall.index)
    diagnosis[d.flag.astype(bool)] = "drift"
    diagnosis[(~d.flag.astype(bool)) & (overall < 0.85)] = "steady-low"
    # END SOLUTION
except NotImplementedError:
    overall = g.groupby("rater").right.mean()
    team_flag = overall < overall.mean() - 0.10
    diagnosis = pd.Series(B.reference("d2_3_drift")["diagnosis"])
print(pd.DataFrame({"overall": overall.round(3), "team rule": team_flag, "diagnosis": diagnosis}))
B.check(diagnosis["R5"] == "drift" and diagnosis["R6"] == "steady-low", "R5 drifts, R6 is steadily low")

# %% [markdown]
# 🔍 The responses differ: R6 needs coaching and stays on double labelling; R5's labels since the
# drift began need re-checking, and R5 a conversation about what changed on day 6.

# %%
first_bad = daily.loc["R5"][daily.loc["R5"] < 0.75].index.min()
print("R5's first day below 0.75:", first_bad)
recheck = ops[(ops.rater == "R5") & (ops.is_gold == 0) & (ops.day >= first_bad)]
print("R5 work labels to re-check:", len(recheck))

# %% [markdown]
# ## 4 · Workload and distressing-content minutes (7')
#
# The guideline limits distressing content to 60 minutes per rater per day. Workload is also worth
# watching: labels per hour.
#
# ✏️ **Exercise** · Minutes of distressing content per rater and day; list the days over the limit.
# Then labels per hour per rater.

# %%
LIMIT_MIN = 60
try:
    # BEGIN SOLUTION
    dist = ops[ops.distressing == 1].groupby(["rater", "day"]).seconds.sum().div(60).round(1)
    over = dist[dist > LIMIT_MIN]
    per_hour = (ops.groupby("rater").size() / ops.groupby("rater").seconds.sum() * 3600).round(1)
    # END SOLUTION
except NotImplementedError:
    dist = ops[ops.distressing == 1].groupby(["rater", "day"]).seconds.sum().div(60).round(1)
    over = dist[dist > LIMIT_MIN]
    per_hour = (ops.groupby("rater").size() / ops.groupby("rater").seconds.sum() * 3600).round(1)
print("distressing minutes over the limit:\n", over)
print("labels per hour:", per_hour.to_dict())
B.check(list(over.index) == [("R4", 7)], "one breach: R4 on day 7")
(B.art("d2_3") / "drift.json").write_text(json.dumps({"drift": d.T.to_dict(), "diagnosis": diagnosis.to_dict(),
                                                       "first_bad_day_R5": int(first_bad), "recheck": len(recheck),
                                                       "over_limit": {f"{r} day {dd}": m for (r, dd), m in over.items()},
                                                       "per_hour": per_hour.to_dict()}, indent=1, default=float), encoding="utf-8")

# %% [markdown]
# ## ✱ Stretch · What R5 now confuses
#
# Cross-tabulate R5's gold answers against the gold label, before and after day 6.

# %%
try:
    # BEGIN SOLUTION
    r5 = g[g.rater == "R5"].assign(period=lambda x: x.day.map(lambda dd: "days 1-5" if dd <= 5 else "days 6-10"),
                                   gold=lambda x: x.complaint_id.map(gold_bank))
    print(pd.crosstab([r5.period, r5.gold], r5.label))
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Why compare a rater with their own baseline rather than with the team?
#    <details><summary>Answer</summary>A team rule flags whoever is lowest, steady or not; a rater's own baseline shows change, which needs a different response.</details>
# 2. Eight gold questions a day give coarse daily accuracies. How does the rule cope?
#    <details><summary>Answer</summary>It pools days (five for the baseline, three recent) and asks for both a meaningful drop and a test statistic, so one bad day does not flag anyone.</details>
# 3. R4 labelled 69 minutes of distressing content on day 7. Whose problem is it?
#    <details><summary>Answer</summary>The workflow's: routing gave R4 more than the guideline allows. Fix the routing and check on R4.</details>
#
# **Carry forward.** `artifacts/d2_3/drift.json` is a section of the quality-control report.
