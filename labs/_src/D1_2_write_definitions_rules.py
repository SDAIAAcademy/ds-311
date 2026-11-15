# %% [markdown]
# # Lab 1.2 · Guideline v1.0 for six categories
#
# Day 1 · Session 2 (Writing a guideline) · 25 min · AI-tutor: an assistant may explain an error,
# not write the guideline.
#
# You write Bayyin's labelling guideline as data: a definition with includes and excludes for each
# category, decision rules in order, edge cases, notes on dialect and code-switching, and the rule on
# distressing content. The notebook renders it to Markdown, lints it, and tests your decision rules
# on twelve edge cases that Khulood Bin Saedan, the labelling lead, has already decided.
#
# **Reference state.** `data/pilot/edge_cases.csv`: twelve complaints, the facts Khulood read from
# each (0 or 1) and her label. Nothing from Lab 1.1 is needed.
#
# **Tasks**
# - [ ] 1 · Definitions with includes and excludes (7')
# - [ ] 2 · Decision rules in order (6')
# - [ ] 3 · Edge cases and language notes (5')
# - [ ] 4 · Who labels distressing content, and for how long (2')
# - [ ] 5 · Test the rules on twelve edge cases (5')
# - [ ] ✱ Stretch · One Gulf-dialect and one code-switched example per category

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

edge = B.read("pilot/edge_cases.csv")
print(edge[["case", "variety", "expected"]].to_string(index=False))
print("facts:", B.FACTS)

# %% [markdown]
# ## 1 · Definitions with includes and excludes (7')
#
# A definition says what the label **measures**. An include names a case that belongs; an exclude
# names a close case that does not, and where it goes instead. Decide here which question each label
# answers: "what is wrong with the product" or "what did the merchant refuse".
#
# ✏️ **Exercise** · Fill `CATEGORIES` for all six codes. Each needs `definition`, at least one
# `includes` and at least one `excludes` that names another category.

# %%
try:
    # BEGIN SOLUTION
    CATEGORIES = {
        "REFUND": dict(definition="The consumer asked for their money back and the merchant refused or ignored the request.",
                       includes=["a refund refused for a faulty product", "a refund refused for an order that never arrived"],
                       excludes=["a repair refused under warranty: WARRANTY", "a fault with no refund requested: DEFECT"]),
        "DEFECT": dict(definition="The product is faulty, damaged or not as described, and no refund or warranty repair was refused.",
                       includes=["arrived broken", "a different model from the listing"],
                       excludes=["the consumer asked for a refund and was refused: REFUND", "a warranty repair was refused: WARRANTY"]),
        "DELIVERY": dict(definition="The order arrived late or not at all, and no refund was refused.",
                         includes=["delivered days after the promised date", "marked delivered but never received"],
                         excludes=["a refund for the missing order was refused: REFUND"]),
        "PRICE": dict(definition="The consumer was charged more than the price displayed at the point of sale (shelf, app or listing).",
                      includes=["shelf price lower than the till", "app price lower than the invoice"],
                      excludes=["an advert promised a discount and the displayed price matched the charge: AD"]),
        "AD": dict(definition="An advert or offer made a claim the merchant did not honour, and the displayed price was charged.",
                   includes=["advertised discount did not exist", "free installation advertised, then charged"],
                   excludes=["the charge differs from the displayed price: PRICE"]),
        "WARRANTY": dict(definition="The product is under warranty and the merchant or service centre refused the repair or replacement.",
                         includes=["service centre refused a repair within the warranty period"],
                         excludes=["a fault with no warranty claim: DEFECT"]),
    }
    # END SOLUTION
except NotImplementedError:
    CATEGORIES = B.reference("guideline_v1_0")["categories"]
    print("using the reference definitions")

# %%
def lint(categories: dict) -> list[str]:
    """Problems that make a guideline hard to apply. An empty list is a pass."""
    problems = []
    for code in B.CATS:
        c = categories.get(code)
        if not c:
            problems.append(f"{code}: missing"); continue
        if len(c.get("definition", "").split()) < 8:
            problems.append(f"{code}: definition shorter than eight words")
        if not c.get("includes"):
            problems.append(f"{code}: no include")
        if not any(any(o in e for o in B.CATS if o != code) for e in c.get("excludes", [])):
            problems.append(f"{code}: no exclude that names where the case goes instead")
    return problems


print(lint(CATEGORIES) or "lint: clean")
B.check(not lint(CATEGORIES), "every category has a definition, an include and an exclude that points elsewhere")

# %% [markdown]
# ## 2 · Decision rules in order (6')
#
# Overlaps are resolved by **order**: the first rule that applies decides. Write the rules as a
# function of the facts (0 or 1): `asked_refund`, `refund_refused`, `faulty`, `not_as_described`,
# `within_warranty`, `repair_refused`, `late`, `not_delivered`, `charged_more`, `advert_claim`.
#
# ✏️ **Exercise** · Write `decide(f)` and `RULES_TEXT`, the same rules in words, in the same order.

# %%
def decide(f: dict) -> str:
    g = lambda k: int(f.get(k, 0) or 0)
    # BEGIN SOLUTION
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
    # END SOLUTION


RULES_TEXT = [
    "1. A repair or replacement refused under warranty is WARRANTY, whatever else the complaint says.",
    "2. A refund the consumer asked for and was refused is REFUND, even when the product was faulty or never arrived.",
    "3. A faulty, damaged or not-as-described product is DEFECT.",
    "4. A late or missing delivery is DELIVERY.",
    "5. A charge above the displayed price is PRICE, even when an advert was involved.",
    "6. An advert or offer not honoured, at the displayed price, is AD.",
]

# %% [markdown]
# ## 3 · Edge cases and language notes (5')
#
# ✏️ **Exercise** · Add at least four edge cases (a short description, the label and the rule that
# decides it), and notes for Gulf dialect and code-switched text: words that signal a fact.

# %%
try:
    # BEGIN SOLUTION
    EDGE_CASES = [
        dict(case="Broken on arrival and the refund was refused", label="REFUND", rule=2),
        dict(case="Under warranty, repair refused, and the refund also refused", label="WARRANTY", rule=1),
        dict(case="Advert said 50% off; the shelf showed one price and the till charged more", label="PRICE", rule=5),
        dict(case="Order never arrived and the money was not returned", label="REFUND", rule=2),
        dict(case="Late delivery and the product arrived broken", label="DEFECT", rule=3),
    ]
    LANGUAGE_NOTES = {
        "gulf": "خرب = stopped working (faulty); طلبت فلوسي ورفضوا = refund asked and refused; حاسبوني = charged; ما وصل = not delivered",
        "mixed": "refund, warranty, delivery and offer may appear in English inside Arabic: read them as the same facts; 'no refund policy' is a refusal",
        "english": "'money back' is a refund request; 'marked delivered' with nothing received is not delivered",
    }
    # END SOLUTION
except NotImplementedError:
    ref = B.reference("guideline_v1_0")
    EDGE_CASES, LANGUAGE_NOTES = ref["edge_cases"], ref["language_notes"]

# %% [markdown]
# ## 4 · Who labels distressing content, and for how long (2')
#
# Some complaints describe threats or abuse by a merchant's staff. The guideline names who may label
# them and the limit per day, so the workflow of Day 2 can enforce it.
#
# ✏️ **Exercise** · Fill `WELLBEING`.

# %%
try:
    # BEGIN SOLUTION
    WELLBEING = dict(flag="distressing", who="raters who opted in and were briefed by the labelling lead (R2 and R4 in this round)",
                     max_minutes_per_day=60, breaks="a break after every 20 minutes of distressing items",
                     escalation="a complaint that describes a risk to someone's safety goes to the duty officer the same day")
    # END SOLUTION
except NotImplementedError:
    WELLBEING = B.reference("guideline_v1_0")["wellbeing"]
B.check(WELLBEING.get("max_minutes_per_day", 0) > 0 and WELLBEING.get("who"), "who and how long are stated")

# %% [markdown]
# ## 5 · Test the rules on twelve edge cases (5')
#
# A guideline is tested like code: Khulood's twelve decided cases are the test set.

# %%
try:
    got = [decide(r) for r in edge[B.FACTS].astype(int).to_dict("records")]
except NotImplementedError:
    got = [B.apply_rules(r) for r in edge[B.FACTS].astype(int).to_dict("records")]
edge["got"] = got
wrong = edge[edge.got != edge.expected]
print(wrong[["case", "expected", "got", "text"]].to_string(index=False) if len(wrong) else "all twelve as decided")
B.check(len(wrong) == 0, "the decision rules reproduce all twelve decided edge cases")

# %%
GUIDELINE = dict(version="1.0", categories=CATEGORIES, rules=RULES_TEXT, edge_cases=EDGE_CASES,
                 language_notes=LANGUAGE_NOTES, wellbeing=WELLBEING, change_log=[])


def render(g: dict) -> str:
    out = [f"# Bayyin complaint categories · guideline v{g['version']}", "", "## Categories", ""]
    for code, c in g["categories"].items():
        out += [f"### {code}", "", c["definition"], "", "Includes: " + "; ".join(c["includes"]),
                "", "Excludes: " + "; ".join(c["excludes"]), ""]
    out += ["## Decision rules, in order", ""] + g["rules"] + ["", "## Edge cases", ""]
    out += [f"- {e['case']}: **{e['label']}** (rule {e['rule']})" for e in g["edge_cases"]]
    out += ["", "## Language notes", ""] + [f"- {k}: {v}" for k, v in g["language_notes"].items()]
    out += ["", "## Distressing content", ""] + [f"- {k}: {v}" for k, v in g["wellbeing"].items()]
    out += ["", "## Change log", ""] + ([f"- {c}" for c in g["change_log"]] or ["- 1.0: first version"])
    return "\n".join(out) + "\n"


out = B.art("d1_2")
_ = (out / "guideline_v1_0.md").write_text(render(GUIDELINE), encoding="utf-8")
_ = (out / "guideline_v1_0.json").write_text(json.dumps(GUIDELINE, ensure_ascii=False, indent=1), encoding="utf-8")
print(render(GUIDELINE)[:900])

# %% [markdown]
# ## ✱ Stretch · Dialect and code-switched examples
#
# Add to each category one Gulf-dialect and one code-switched example taken from the pilot file
# (`data/pilot/pilot_round1.csv`, filter `variety`).

# %%
try:
    # BEGIN SOLUTION
    pilot = B.read("pilot/pilot_round1.csv")
    for v in ("gulf", "mixed"):
        print(v, pilot[pilot.variety == v].text.head(2).tolist())
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. A complaint says the phone broke and the shop refused a refund. Which rule decides, and why does order matter?
#    <details><summary>Answer</summary>Rule 2, REFUND: the label measures what the merchant refused. Without an order, both REFUND and DEFECT apply and raters split.</details>
# 2. Why must each exclude name the category the case goes to?
#    <details><summary>Answer</summary>An exclude that only says "not this" leaves the rater to guess; naming the destination makes the guideline complete for that overlap.</details>
# 3. Why does a labelling guideline carry a limit on distressing content?
#    <details><summary>Answer</summary>Raters' wellbeing is part of the method: tired or distressed raters label worse, and the workflow can only enforce a limit the guideline states.</details>
#
# **Carry forward.** `artifacts/d1_2/guideline_v1_0.json` is revised in Lab 1.4, which starts from the
# reference guideline when this file is missing.
