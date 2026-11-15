# %% [markdown]
# # Lab 1.4 · Adjudicate 30, revise, measure again
#
# Day 1 · Session 4 (Adjudication and revision) · 25 min · AI-tutor.
#
# Thirty complaints from the first pilot round on which the three raters split. You decide each one
# against the guideline with a reason code, count the reasons, revise the guideline to v1.1 with a
# change log in which every entry cites a measured disagreement, and compare agreement in round 1
# with round 2, which the raters labelled under v1.1.
#
# **Reference state.** `data/pilot/disagreements30.csv` (the three labels and the facts the
# adjudicator reads), `data/pilot/pilot_round1.csv` and `pilot_round2.csv`, and guideline v1.0 from
# Lab 1.2 or its reference copy.
#
# **Tasks**
# - [ ] 1 · Sort the 30 disagreements by category pair (5')
# - [ ] 2 · Adjudicate: a decision and a reason code each (8')
# - [ ] 3 · Guideline v1.1: a change log tied to the counts (7')
# - [ ] 4 · Round 2: did agreement rise, and where (5')
# - [ ] ✱ Stretch · How often was the majority of three raters wrong?

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

import pandas as pd
import bayyin as B

dis = B.read("pilot/disagreements30.csv")
own = B.ART / "d1_2" / "guideline_v1_0.json"
guide = json.loads(own.read_text(encoding="utf-8")) if own.exists() else B.reference("guideline_v1_0")
print(len(dis), "disagreements; guideline", guide["version"], "from", "Lab 1.2" if own.exists() else "the reference copy")

# %% [markdown]
# ## 1 · Sort the disagreements by category pair (5')
#
# ✏️ **Exercise** · For each complaint, the set of labels the raters gave, as a sorted string
# (`DEFECT|REFUND`). Count them.

# %%
def label_set(row) -> str:
    # BEGIN SOLUTION
    return "|".join(sorted({row.R1, row.R2, row.R3}))
    # END SOLUTION


try:
    dis["labels"] = dis.apply(label_set, axis=1)
except NotImplementedError:
    dis["labels"] = dis.apply(lambda r: "|".join(sorted({r.R1, r.R2, r.R3})), axis=1)
pairs = dis["labels"].value_counts()
print(pairs.to_string())

# %% [markdown]
# ## 2 · Adjudicate: a decision and a reason code each (8')
#
# The adjudicator does not vote: she reads the complaint, applies the guideline's rules in order, and
# records why. Reason codes:
# - `RULE_ORDER`: two categories applied and the rule order decided
# - `MISREAD`: a rater missed a fact in the text (often in dialect or code-switched text)
# - `DEFINITION`: the definition did not cover the case: the guideline must change
#
# ✏️ **Exercise** · Write `adjudicate(row)` returning `(decision, reason)` from the facts columns.
# Use the decision rules (`B.apply_rules` is guideline v1.1's version; yours from Lab 1.2 is fine).

# %%
def adjudicate(row) -> tuple[str, str]:
    # BEGIN SOLUTION
    facts = {k: int(row[k]) for k in B.FACTS}
    decision = B.apply_rules(facts)
    applicable = {c for c, ks in {"REFUND": ["refund_refused"], "DEFECT": ["faulty", "not_as_described"],
                                  "DELIVERY": ["late", "not_delivered"], "PRICE": ["charged_more"], "AD": ["advert_claim"],
                                  "WARRANTY": ["repair_refused"]}.items() if any(facts[k] for k in ks)}
    if len(applicable) > 1:
        reason = "DEFINITION" if decision == "WARRANTY" else "RULE_ORDER"
    else:
        reason = "MISREAD"
    return decision, reason
    # END SOLUTION


try:
    res = dis.apply(adjudicate, axis=1, result_type="expand")
    dis["decision"], dis["reason"] = res[0], res[1]
except NotImplementedError:
    ref = B.read("reference/adjudicator_decisions.csv")
    dis = dis.merge(ref, on="complaint_id")
    dis["reason"] = "RULE_ORDER"
khulood = B.read("reference/adjudicator_decisions.csv").set_index("complaint_id").decision
agree_k = (dis.set_index("complaint_id").decision == khulood).mean()
print(dis.reason.value_counts().to_dict(), "| matches the labelling lead on", f"{agree_k:.0%}")
B.check(agree_k == 1.0, "every decision matches the labelling lead's")
dis[["complaint_id", "variety", "R1", "R2", "R3", "decision", "reason"]].to_csv(B.art("d1_4") / "adjudicated30.csv", index=False)

# %% [markdown]
# ## 3 · Guideline v1.1: a change log tied to the counts (7')
#
# Every change cites what was measured: which pair, how many of the 30, and the rule or definition
# that changes. A change nobody can trace to a disagreement is an opinion.
#
# ✏️ **Exercise** · Count disagreements by pair and reason, then write `CHANGES`, at least three
# entries of the form `"v1.1: <what changed> (<evidence>)"`.

# %%
by = dis.groupby(["labels", "reason"]).size().sort_values(ascending=False)
print(by.to_string())
r3_warranty = int(((dis.R1 == "WARRANTY") & (dis.R3 == "DEFECT")).sum())
print("R3 said DEFECT where R1 said WARRANTY:", r3_warranty)

# %%
try:
    # BEGIN SOLUTION
    n = lambda pair: int((dis["labels"] == pair).sum())
    CHANGES = [
        f"v1.1: rule 2 example added, 'broken and refund refused is REFUND' (DEFECT|REFUND split {n('DEFECT|REFUND')} of 30)",
        f"v1.1: DEFECT excludes now names WARRANTY first, with the Gulf wording 'لسا عليه ضمان' (WARRANTY|DEFECT split {n('DEFECT|WARRANTY')} of 30; R3 said DEFECT {r3_warranty} times)",
        f"v1.1: rule 5 restated as 'compare the charge with the displayed price before reading the advert' (AD|PRICE split {n('AD|PRICE')} of 30)",
        f"v1.1: language notes add code-switched 'refund' and 'no refund policy' as a refusal (MISREAD {int((dis.reason == 'MISREAD').sum())} of 30)",
    ]
    # END SOLUTION
except NotImplementedError:
    CHANGES = ["v1.1: not written yet"]
guide_11 = dict(guide, version="1.1", change_log=guide.get("change_log", []) + CHANGES)
_ = (B.art("d1_4") / "guideline_v1_1.json").write_text(json.dumps(guide_11, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n".join(CHANGES))
B.check(len(CHANGES) >= 3 and all("of 30" in c for c in CHANGES), "every change cites a count")

# %% [markdown]
# ## 4 · Round 2: did agreement rise, and where (5')
#
# The raters labelled the same 300 complaints again under v1.1 (round 2). Compare alpha by category
# and variety. A revision that worked shows up where the change log said it would.

# %%
r2 = B.read("pilot/pilot_round2.csv")
r1 = B.read("pilot/pilot_round1.csv")
R = ["R1", "R2", "R3"]


def by_cat(df):
    u = df[R].values.tolist()
    return {c: round(B.krippendorff_alpha([[int(x == c) for x in row] for row in u]), 3) for c in B.CATS}


cmp = pd.DataFrame({"round 1": by_cat(r1), "round 2": by_cat(r2)})
cmp.loc["ALL"] = [round(B.krippendorff_alpha(r1[R].values.tolist()), 3), round(B.krippendorff_alpha(r2[R].values.tolist()), 3)]
for v in B.VARIETIES:
    cmp.loc[f"variety {v}"] = [round(B.krippendorff_alpha(d[d.variety == v][R].values.tolist()), 3) for d in (r1, r2)]
print(cmp.to_string())
lo, hi = B.bootstrap(B.krippendorff_alpha, r2[R].values.tolist(), B.pick(1000, 200))
print("round 2 alpha 95% interval:", lo, hi)
B.check(cmp.loc["ALL", "round 2"] > cmp.loc["ALL", "round 1"] + 0.15, "alpha rose by more than 0.15")
cmp.to_csv(B.art("d1_4") / "agreement_r1_r2.csv")

# %% [markdown]
# ## ✱ Stretch · Was the majority right?
#
# In how many of the 30 did two raters agree, and how often was that majority **not** the
# adjudicated decision?

# %%
try:
    # BEGIN SOLUTION
    maj = dis.apply(lambda r: Counter([r.R1, r.R2, r.R3]).most_common(1)[0], axis=1)
    has_maj = maj.apply(lambda m: m[1] >= 2)
    wrong = (maj.apply(lambda m: m[0]) != dis.decision) & has_maj
    print(int(has_maj.sum()), "had a majority;", int(wrong.sum()), "majorities were wrong")
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Two raters said DEFECT and one said REFUND; the text says the refund was refused. What is the adjudicated label, and why not the majority?
#    <details><summary>Answer</summary>REFUND, by rule 2. A majority of people who applied the same wrong reading is still wrong; adjudication applies the guideline.</details>
# 2. What makes a change-log entry acceptable?
#    <details><summary>Answer</summary>It names what changed and the measured disagreement that caused it, so the next round can show whether it worked.</details>
# 3. Round 2 alpha rose overall but stayed lowest for mixed text. What do you report?
#    <details><summary>Answer</summary>Both: the overall gain and the variety where labels are still least reliable, with its interval, so analysts weigh those complaints accordingly.</details>
#
# **Carry forward.** `artifacts/d1_4/guideline_v1_1.json` and `agreement_r1_r2.csv` feed the
# datasheet in Lab 4.4, which reads reference copies when they are missing.
