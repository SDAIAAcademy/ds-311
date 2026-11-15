# %% [markdown]
# # Lab 2.4 · Cost per accepted label
#
# Day 2 · Session 4 (Cost and model pre-labels) · 25 min · AI-tutor.
#
# Hatoon asks what a label costs and whether a model could make it cheaper. First, nothing leaves
# the office before personal data is masked and the record is classified: Rihab Al-Mudaimeegh, the
# data protection officer, has ruled that raw complaint text is **Restricted** and that masked text
# with no identifier left may be sent to the approved free hosted model for pre-labels. Then you send
# masked complaints through a chat-completions endpoint (Fahis, the pre-labelling step), and compare
# three labelling designs on a trial of 300 gold complaints: cost per accepted label and error.
#
# **Reference state.** `data/ops/to_prelabel.csv` (40 complaints, most with personal data) and
# `data/ops/design_trial.csv` (300 gold complaints labelled under each of three designs, with
# seconds per label). Without a model key the endpoint calls go to a scripted stand-in, and the
# notebook says so.
#
# **Tasks**
# - [ ] 1 · Mask personal data; classify what may leave (7')
# - [ ] 2 · Pre-label masked complaints through the endpoint (5')
# - [ ] 3 · Cost and error of three designs (9')
# - [ ] 4 · Choose a design, and the condition that would change it (4')
# - [ ] ✱ Stretch · Anchoring: how often do people confirm a wrong pre-label?

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
import re
import pandas as pd
import bayyin as B

items = B.read("ops/to_prelabel.csv")
print(len(items), "complaints to pre-label; model:", B.MODEL)
print(items.text.iloc[0])

# %% [markdown]
# ## 1 · Mask personal data; classify what may leave (7')
#
# ✏️ **Exercise** · Write `mask(text)`: replace IBANs, e-mail addresses, mobile numbers and national
# ID numbers with `[IBAN]`, `[EMAIL]`, `[PHONE]`, `[NATIONAL_ID]`. Then `classify(masked)`: `"Restricted"`
# when anything that looks like an identifier is left (seven or more digits in a row, in Latin **or
# Arabic-Indic** digits: `B.residual_digits`), otherwise `"Masked: may be sent"`.

# %%
def mask(text: str) -> str:
    # BEGIN SOLUTION
    t = text.translate(B.TO_LATIN)  # Arabic-Indic digits to Latin first, so one pattern sees both
    for name in ["IBAN", "EMAIL", "PHONE", "NATIONAL_ID"]:
        t = re.sub(B.PII_PATTERNS[name], f"[{name}]", t)
    return t
    # END SOLUTION


def classify(masked: str) -> str:
    # BEGIN SOLUTION
    return "Restricted" if B.residual_digits(masked) or "@" in masked else "Masked: may be sent"
    # END SOLUTION


try:
    items["masked"] = items.text.map(mask)
    items["class"] = items.masked.map(classify)
except NotImplementedError:
    items["masked"] = items.text
    items["class"] = "Restricted"
    print("mask() not written: every complaint stays Restricted and nothing is sent")
naive = items.text.map(lambda t: re.sub(r"05\d{8}", "[PHONE]", t))
print(items["class"].value_counts().to_dict())
print("a naive Latin-digit pattern leaves", int(naive.map(B.residual_digits).sum()), "complaints with an identifier")
B.check((items["class"] == "Masked: may be sent").sum() >= 38, "at least 38 of 40 complaints are safe to send after masking")
print(items.masked.iloc[0])

# %% [markdown]
# 🔍 **Look at** the complaints whose phone numbers are written in Arabic-Indic digits (`٠٥…`). A pattern
# written for Latin digits passes them through untouched.

# %% [markdown]
# ## 2 · Pre-label masked complaints through the endpoint (5')
#
# Only complaints classified `Masked: may be sent` go out. `B.chat` sends one chat-completions request
# (OpenRouter by default), replays identical requests from `labs/cache/`, and falls back to a scripted
# stand-in when no key works; `B.LAST_SOURCE` says which answered.
#
# ✏️ **Exercise** · Write the prompt and `prelabel(masked)` that returns one of the six codes.

# %%
SYSTEM = ("You label consumer complaints for a consumer protection office. Reply with exactly one code: "
          "REFUND, DEFECT, DELIVERY, PRICE, AD or WARRANTY. Rules in order: warranty repair refused is WARRANTY; "
          "refund asked and refused is REFUND; faulty or not as described is DEFECT; late or missing delivery is "
          "DELIVERY; charged above the displayed price is PRICE; an advert or offer not honoured is AD.")


def prelabel(masked: str) -> str:
    # BEGIN SOLUTION
    reply = B.chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": masked}], max_tokens=8)
    code = re.sub(r"[^A-Z]", "", reply.upper())
    return next((c for c in B.CATS if c in code), "UNPARSED")
    # END SOLUTION


send = items[items["class"] == "Masked: may be sent"].head(B.pick(20, 12))
sources = []
try:
    pre = []
    for t in send.masked:
        pre.append(prelabel(t))
        sources.append(B.LAST_SOURCE["source"])
except NotImplementedError:
    pre = [B.stand_in([{"content": t}]) for t in send.masked]
    sources = ["stand-in"] * len(pre)
send = send.assign(prelabel=pre, answered_by=sources)
truth = B.expert_labels(send.complaint_id)
acc = (send.prelabel.values == truth.values).mean()
print(send[["complaint_id", "variety", "prelabel", "answered_by"]].to_string(index=False))
print(f"pre-label accuracy on these {len(send)}: {acc:.2f} | answered by: {sorted(set(sources))}")
if "stand-in" in sources:
    print("⚠️ the scripted stand-in answered: these are keyword rules, not a model's labels")
B.check(not any("@" in t or B.residual_digits(t) for t in send.masked), "nothing Restricted was sent")

# %% [markdown]
# ## 3 · Cost and error of three designs (9')
#
# The trial labelled the same 300 gold complaints three ways:
# - **double**: two raters each; disagreements adjudicated;
# - **audited single**: one rater; about 15% get a second label as an audit; audit disagreements adjudicated;
# - **model-assisted**: a masked pre-label, and a person who confirms or corrects **every** one.
#
# Rates: raters SAR 60 an hour, the adjudicator SAR 120 an hour and 90 seconds an item; the free
# model tier costs nothing per call here (a paid model would add its token price).
#
# ✏️ **Exercise** · Per design: total cost, cost per accepted label (every final label is accepted
# after the design's own checks) and error of the accepted labels against gold.

# %%
trial = B.read("ops/design_trial.csv", dtype={"seconds_1": int, "seconds_2": int, "adjudicated": int, "audited": int})
RATER, ADJ, ADJ_SEC = 60 / 3600, 120 / 3600, 90


def design_table(trial: pd.DataFrame) -> pd.DataFrame:
    # BEGIN SOLUTION
    rows = []
    for name, d in trial.groupby("design", sort=False):
        cost = (d.seconds_1 + d.seconds_2).sum() * RATER + d.adjudicated.sum() * ADJ_SEC * ADJ
        rows.append(dict(design=name, labels=len(d), cost_sar=round(cost, 1), sar_per_label=round(cost / len(d), 3),
                         error=round((d.final != d.gold_label).mean(), 3), adjudicated=int(d.adjudicated.sum())))
    return pd.DataFrame(rows).set_index("design")
    # END SOLUTION


try:
    designs = design_table(trial)
except NotImplementedError:
    designs = pd.DataFrame(B.reference("d2_4_designs")).T
print(designs)
B.check(designs.sar_per_label.idxmin() == "model_assisted" and designs.error.idxmin() == "double", "model-assisted is cheapest, double labelling most accurate")
(B.art("d2_4") / "designs.json").write_text(designs.T.to_json(indent=1), encoding="utf-8")

# %% [markdown]
# ## 4 · Choose a design, and the condition that would change it (4')
#
# ✏️ **Exercise** · Hatoon's analysts accept at most 5% wrong labels. Pick the cheapest design under
# that error, and write the condition that would make you change it.

# %%
MAX_ERROR = 0.05
try:
    # BEGIN SOLUTION
    ok = designs[designs.error <= MAX_ERROR]
    choice = ok.sar_per_label.idxmin() if len(ok) else designs.error.idxmin()
    CONDITION = (f"{choice} at SAR {designs.loc[choice, 'sar_per_label']} a label and {designs.loc[choice, 'error']:.1%} error. "
                 "Switch to model-assisted only if its error falls to 5% or less on a new trial (for example after a "
                 "better pre-label prompt or a check that stops people confirming a wrong pre-label), measured by "
                 "language variety; DS-306 covers measuring the model's own labels.")
    # END SOLUTION
except NotImplementedError:
    choice, CONDITION = "double", "not written yet"
print("choice:", choice)
print(CONDITION)

# %% [markdown]
# ## ✱ Stretch · Anchoring
#
# Among model-assisted items whose pre-label was wrong, how often did the person confirm it?

# %%
try:
    # BEGIN SOLUTION
    ma = trial[trial.design == "model_assisted"]
    wrong_pre = ma[ma.prelabel != ma.gold_label]
    print(f"{len(wrong_pre)} wrong pre-labels; confirmed by the person: {(wrong_pre.final == wrong_pre.prelabel).mean():.0%}")
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Why translate Arabic-Indic digits before matching phone and ID numbers?
#    <details><summary>Answer</summary>Complainants write numbers in both digit sets; a pattern for Latin digits sends the others out untouched, and the record leaves the office Restricted.</details>
# 2. The model-assisted design is cheapest. Why is it not the choice here?
#    <details><summary>Answer</summary>Its error is above the analysts' limit, mostly because people confirm wrong pre-labels; cost per accepted label is only comparable between designs that meet the error limit.</details>
# 3. Who decides that masked text may be sent to a hosted model?
#    <details><summary>Answer</summary>The data owner with the data protection officer, under the classification policy, not the analyst who finds it convenient.</details>
#
# **Carry forward.** `artifacts/d2_4/designs.json` completes the quality-control report: the flagged
# rater, the queues and the cost per accepted label.
