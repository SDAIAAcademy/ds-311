---
course: "Data Quality, Labelling and Pipelines for Analysis"
code: "DS-311"
version: "2027.1.0"
deck: "day1"
day: 1
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-311/slides/day1.html"
---

# Data Quality, Labelling and Pipelines for Analysis

## Day 1: Labels are measurements

Write, pilot and measure a labelling guideline

#### [day1#title] Labels are measurements

*SDAIA Academy · Data Quality, Labelling and Pipelines for Analysis*

Day 1: Write, pilot and measure a labelling guideline

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-311

#### [day1#four-days-one-table] Four days build the table an analysis depends on

*The course at a glance*

- **Day 1 · Labels.** A guideline, a pilot, agreement, adjudication and a revision.
- **Day 2 · Operations.** A golden set, gold checks, review queues, drift and cost.
- **Day 3 · Rules.** Profiles, severity rules, merchant matching and a contract.
- **Day 4 · Pipelines.** Steps, gates, lineage, a changed figure and a datasheet.

> **Day 5 · Capstone.** A labelled, quality-gated table for a second case, in a public repository, reviewed live while the assessor seeds a defect.

#### [day1#measure-then-decide] Every claim about the data is measured before it is trusted

*How this course works*

- **Labels are measurements.** They have a construct, an instrument and an error, like any other measurement.
- **Rules have owners.** A threshold is a business decision someone signs, not a default in a library.
- **Runs leave evidence.** Run logs and lineage answer "why did this number change" without guessing.

> **AI policy.** AI off for the supervised check and for the first lab of Day 1 and Day 3. In the other labs an assistant may explain an error but not write the guideline or the rules. In the capstone anything goes, and model pre-labels are always checked by a person.

#### [day1#bayyin-office] Bayyin Consumer Protection Office and its complaints

*One case study all week*

A fictional regulator with 30,000 synthetic complaints in Arabic and English. Its analysts publish a monthly complaint rate per 100,000 residents by region.

- **Hatoon Al-Furaih.** Head of market monitoring. Owns the monthly rate.
- **Khulood Bin Saedan.** Labelling lead and adjudicator.
- **Abdulelah Al-Batal.** Data engineer. Owns the preparation pipeline.
- **Rihab Al-Mudaimeegh.** Data protection officer.

#### [day1#what-the-data-holds] Four kinds of data, one seed

*What you will work with*

| Data | Size | Used on |
| --- | --- | --- |
| Complaint texts in MSA, Gulf dialect, English and mixed | 30,000 | Days 1 and 2 |
| Pilot labels: three raters, two rounds | 300 x 3 x 2 | Day 1 |
| An operations round: six raters over ten days | 2,986 labels | Day 2 |
| Four source tables with seeded defects | 30,300 rows | Days 3 and 4 |
| Two pipeline runs with lineage records | 2 runs | Day 4 |

About 18% of the texts carry planted personal data (phone numbers, e-mail addresses, ID numbers, IBANs). It is masked before any model call on Day 2.

#### [day1#setup-check] Clone, sync, run the setup check

*Lab environment*

1. Every lab starts from a **supplied reference state**: a file in `labs/data/`. No lab needs an earlier one.
2. Run `00_setup_check.ipynb` once. It imports every package and reads one file of each kind.
3. One lab on Day 2 calls a free hosted model. Without a key it runs on a scripted stand-in.

```bash
# file: terminal (local option)
git clone https://github.com/SDAIAAcademy/ds-311
cd ds-311/labs
uv sync
uv run jupyter lab
```

#### [day1#agenda] Labels are measurements

*Today*

- **Session 1 · What a label measures**: A label is a measurement of a construct, and disagreement shows where the construct is unclear
- **Session 2 · Writing a guideline**: Definitions, ordered decision rules, edge cases and the rules for raters' wellbeing, written as a versioned document
- **Session 3 · Agreement statistics**: Percent agreement, Cohen's kappa and Krippendorff's alpha, by category, rater and language, with intervals
- **Session 4 · Adjudication and revision**: Disagreements decided against the guideline with a reason, and a revision that the next round measures

### Session 1: What a label measures

#### [day1#s1] What a label measures

*Session 1*

- Explain a label as a measurement with a construct, a scale and an error
- Label complaints without a guideline and measure raw agreement with two neighbours
- Name the category pairs where people disagree and why

#### [day1#label-is-a-measurement] A label is a measurement, with a construct and an error

*What a label is*

- **Construct.** What the label is meant to capture: "what the merchant refused", not "what went wrong".
- **Instrument.** A person reading text under a guideline. Change the guideline and you change the instrument.
- **Error.** Two people reading the same complaint give different labels. That spread is measurable.

> **So.** A complaint rate by category is only as reliable as the labels under it. The analyst who publishes it owns that reliability.

#### [day1#labels-feed-decisions] Labels become figures, and figures become enforcement

*Why it matters at Bayyin*

1. **1 · Complaint** free text, any dialect
2. **2 · Label** one of six categories
3. **3 · Figure** rate by category, region, merchant
4. **4 · Action** inspection, warning, public notice

If raters split REFUND and DEFECT differently from month to month, a rise in refund refusals can be a change of raters, not of merchants.

#### [day1#six-categories] Six categories, and the overlaps already visible

*The label schema*

| Code | Short name | Overlaps with |
| --- | --- | --- |
| **REFUND** | refund refused | DEFECT, DELIVERY |
| **DEFECT** | defective or not as described | REFUND, WARRANTY |
| **DELIVERY** | late or missing delivery | REFUND |
| **PRICE** | charged more than displayed | AD |
| **AD** | misleading advert or offer | PRICE |
| **WARRANTY** | warranty or repair refused | DEFECT |

#### [day1#one-complaint-two-labels] A broken product and a refused refund: which is it?

*The same text, two honest readings*

**Complaint C103462, Gulf dialect:** شريت خزانة من الفارس للأثاث المحدودة. خرب بعد 5 أيام. طلبت فلوسي ورفضوا.

- **Rater who says DEFECT.** Measured "what is wrong with the product".
- **Rater who says REFUND.** Measured "what did the merchant refuse".

> **Neither rater is careless.** The schema has not said which question the label answers.

#### [day1#disagreement-is-signal] Disagreement shows where the construct is unclear

*What to do with a split*

- **Random** disagreement: tiredness, a misread word. It spreads over every pair of categories.
- **Systematic** disagreement: two readings of the schema. It piles up on one pair, such as DEFECT and REFUND.
- Systematic splits are fixed by the **guideline**; random ones by training, workload and checks.
- Some items are genuinely ambiguous: record them as edge cases rather than forcing a vote.

#### [day1#forty-complaint-splits] On 40 complaints, three people agreed on 26

*The example colleague in Lab 1.1*

| Item | Value |
| --- | --- |
| DEFECT and REFUND | 6 |
| AD and PRICE | 6 |
| DEFECT and DELIVERY | 4 |
| DELIVERY and REFUND | 4 |
| AD and DELIVERY | 2 |

**0.68 to 0.85** pairwise percent agreement

Pairs of people who disagreed, counted by the two categories they gave.

#### [day1#annotation-tools] The tool records labels; it does not define them

*Where labelling happens*

- **Annotation platforms.** Label Studio, Argilla: queues, several raters per item, export with rater ids.
- **A locked spreadsheet.** Validation lists for the codes, protected columns, one sheet per rater.
- **What all need.** Rater id, item id, guideline version and time spent on every label.

This week's labs use files with those four fields, so every number can be recomputed on a laptop.

#### [day1#checkpoint-1] What does a pile of splits on one pair tell you?

*Checkpoint*

**Question:** In a pilot, 70% of all disagreements fall on DEFECT against REFUND, and the rest spread thinly. What is the most likely cause?

- A. The schema does not say which question the label answers
- B. The raters were tired and misread the texts
- C. One rater needs retraining on the six codes
- D. The pilot is too small to show anything

#### [day1#lab-1-1] Label 40 complaints, then compare

Lab 1.1 · 25 min

Label 40 complaints with only the six category names (AI-off), compare with two neighbours' labels, and find the category pairs and complaints that split you.

[D1_1_label_40_complaints.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D1_1_label_40_complaints.ipynb)

- [ ] Label 40 complaints with only the six category names (12 min)
- [ ] Load two neighbours' labels (3 min)
- [ ] Percent agreement and the pairs that split you (5 min)
- [ ] Three disagreements: what each of you measured (5 min)
- [ ] ✱ Stretch: Agreement by language variety: Arabic, Gulf dialect, English, mixed

### Session 2: Writing a guideline

#### [day1#s2] Writing a guideline

*Session 2*

- Write a definition with includes and excludes for each category
- Order decision rules so that every overlap resolves to one label
- Record edge cases, dialect notes and the limits on distressing content

#### [day1#guideline-parts] A guideline is the instrument, written down

*What a labelling guideline holds*

- **Definitions.** What each label measures, with includes and excludes.
- **Decision rules.** An order that resolves every overlap to one label.
- **Edge cases.** Decided examples raters can match against.
- **Language notes.** Dialect words and code-switching that signal a fact.
- **Wellbeing.** Who labels distressing content, and for how long.
- **Version and change log.** Every label records the version it was made under.

#### [day1#definition-with-excludes] An exclude names where the case goes instead

*Writing a definition*

| Part | DEFECT in guideline v1.0 |
| --- | --- |
| **Definition** | The product is faulty, damaged or not as described, and no refund or warranty repair was refused. |
| **Includes** | arrived broken; a different model from the listing |
| **Excludes** | a refund asked and refused: **REFUND**; a warranty repair refused: **WARRANTY** |

> **What goes wrong.** "Excludes: other issues" leaves the rater to guess. The lab's lint fails an exclude that does not name another code.

#### [day1#decision-rules-in-order] The first rule that applies decides

*Resolving overlaps*

1. A repair refused under warranty is **WARRANTY**, whatever else the complaint says.
2. A refund asked for and refused is **REFUND**, even when the product was faulty or never arrived.
3. A faulty, damaged or not-as-described product is **DEFECT**.
4. A late or missing delivery is **DELIVERY**.
5. A charge above the displayed price is **PRICE**, even when an advert was involved.
6. An advert or offer not honoured, at the displayed price, is **AD**.

#### [day1#rules-as-code] Write the rules as code, and test them like code

*Lab 1.2*

```python
# file: decide(f)
def decide(f):
    if f["within_warranty"] and f["repair_refused"]:
        return "WARRANTY"
    if f["asked_refund"] and f["refund_refused"]:
        return "REFUND"
    if f["faulty"] or f["not_as_described"]:
        return "DEFECT"
    ...
```

- **Facts, not words.** Ten yes-or-no facts a reader takes from the text, in any language.
- **A test set.** Twelve edge cases Khulood already decided. All twelve must pass.

#### [day1#dialect-and-code-switching] The same fact, written four ways

*Language notes*

| Variety | "I asked for a refund and they refused" |
| --- | --- |
| MSA | طلبت استرداد المبلغ فرفضوا. |
| Gulf dialect | طلبت فلوسي ورفضوا. |
| Mixed | طلبت refund ورفضوا. |
| English | I asked for a refund and they refused. |

About 28% of Bayyin's complaints are in Gulf dialect and 6% mix Arabic and English. A guideline written only for MSA leaves a third of the corpus to guesswork.

#### [day1#distressing-content-rule] The guideline says who labels distressing content, and for how long

*Responsible labelling*

- About 3% of complaints describe threats or abuse by a merchant's staff.
- Only raters who opted in and were briefed label them.
- A daily limit, 60 minutes at Bayyin, and a break after every 20.
- A risk to someone's safety goes to the duty officer the same day.

- **Why in the guideline.** A limit nobody wrote down cannot be enforced or checked. On Day 2 you check it from the workload log.

#### [day1#guideline-versions] Every label carries the guideline version it was made under

*A guideline changes*

1. **v0.1** category names only: pilot round 1
2. **v1.0** definitions, rules, edge cases: Lab 1.2
3. **v1.1** revised from adjudication: Lab 1.4, pilot round 2

> **Rule of thumb.** A change that alters what a label means needs a new version; old labels are re-checked or flagged, never silently mixed.

#### [day1#checkpoint-2] Which rule decides this complaint?

*Checkpoint*

**Question:** "The washing machine is still under warranty. The service centre refused to repair it, and the shop also refused my refund." Under guideline v1.0, which label?

- A. REFUND, because the refund refusal is the last fact stated
- B. DEFECT, because the machine is faulty
- C. WARRANTY, because rule 1 applies first
- D. None: it must go to adjudication

#### [day1#lab-1-2] Guideline v1.0 for six categories

Lab 1.2 · 25 min

Write guideline v1.0 as data, render it to Markdown, lint it for missing parts, and test its decision rules on twelve edge cases.

[D1_2_write_definitions_rules.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D1_2_write_definitions_rules.ipynb)

- [ ] Definitions with includes and excludes (7 min)
- [ ] Decision rules in order (6 min)
- [ ] Edge cases and language notes (5 min)
- [ ] Who labels distressing content, and for how long (2 min)
- [ ] Test the rules on twelve edge cases (5 min)
- [ ] ✱ Stretch: One Gulf-dialect and one code-switched example per category

### Session 3: Agreement statistics

#### [day1#s3] Agreement statistics

*Session 3*

- Compute kappa for each pair of raters and explain the chance correction
- Compute Krippendorff's alpha from a coincidence matrix
- Report agreement by category and language with bootstrap intervals

#### [day1#percent-agreement-flatters] Percent agreement counts luck as skill

*The first number everyone computes*

- **0.54** all three raters agree, round 1
- **0.65 to 0.70** agreement of each pair
- **0.20** pair agreement expected by chance

Chance agreement for two raters is the sum over categories of pa(c) x pb(c): how often they would match if each labelled at random with their own frequencies.

#### [day1#prevalence-paradox] With a dominant category, 90% agreement can be worth nothing

*Why chance correction matters*

|  | Rater A says "yes" 90% | Rater B says "yes" 90% |
| --- | --- | --- |
| Agreement by chance | 0.9 x 0.9 + 0.1 x 0.1 = 0.82 |  |
| Observed agreement | 0.90 |  |
| Kappa | (0.90 - 0.82) / (1 - 0.82) = 0.44 |  |

> **What goes wrong.** A rare category such as WARRANTY looks reliable on percent agreement because both raters almost always say "no".

#### [day1#cohen-kappa] Kappa: the share of possible agreement above chance

*Two raters*

```python
# file: Lab 1.3
def kappa(a, b):
    po = mean(x == y for x, y in zip(a, b))
    pe = chance_agreement(a, b)
    return (po - pe) / (1 - pe)
```

| Item | Value |
| --- | --- |
| R1 and R2 | 0.601 |
| R1 and R3 | 0.619 |
| R2 and R3 | 0.564 |

Cohen's kappa compares exactly two raters, each labelling every item. Three raters give three kappas.

#### [day1#krippendorff-alpha] Krippendorff's alpha compares observed with expected disagreement

*Any number of raters, missing labels allowed*

1. Each complaint with m labels adds 1/(m-1) to the cell of every ordered pair of its labels.
2. Do: the off-diagonal share of that coincidence matrix.
3. De: the disagreement expected from the label totals alone.
4. alpha = 1 - Do / De

**0.594** alpha, round 1, three raters, 300 complaints

- A rater who skipped twenty complaints changes it only to 0.591: alpha uses whatever labels each item has.

#### [day1#coincidence-matrix] The off-diagonal cells name the pairs to fix

*Reading the matrix*

| Largest off-diagonal pairs, round 1 | Weight | The guideline rule that should separate them |
| --- | --- | --- |
| DEFECT and REFUND | 36.5 | rule 2: a refused refund is REFUND |
| WARRANTY and DEFECT | 20.0 | rule 1: warranty first |
| DELIVERY and REFUND | 19.5 | rule 2: a refused refund is REFUND |
| PRICE and AD | 14.5 | rule 5: compare the charge with the displayed price |

Of 40 WARRANTY labels in round 1, the coincidences put 20 against DEFECT and only 8 on WARRANTY itself.

#### [day1#alpha-by-category] One category is barely above chance

*Lab 1.3, by category, with 95% intervals*

| Category | Labels | Alpha | Interval |
| --- | --- | --- | --- |
| DELIVERY | 221 | 0.736 | 0.663 to 0.807 |
| AD | 118 | 0.678 | 0.577 to 0.764 |
| PRICE | 87 | 0.593 | 0.437 to 0.703 |
| DEFECT | 241 | 0.575 | 0.473 to 0.653 |
| REFUND | 193 | 0.512 | 0.422 to 0.589 |
| WARRANTY | 40 | 0.164 | 0.061 to 0.267 |

#### [day1#alpha-by-variety] Agreement is lowest where the language is least standard

*Lab 1.3, by language variety*

| Item | Value |
| --- | --- |
| English (55) | 0.674 |
| MSA (136) | 0.669 |
| Gulf dialect (94) | 0.470 |
| Mixed (15) | 0.340 |

> **Fifteen mixed complaints give an interval from 0.11 to 0.54.** Report it, and say it is too wide to rank.

#### [day1#agreement-report] Report the number, its interval, and where it is weak

*What the agreement report says*

- Overall alpha with a bootstrap interval over items.
- Alpha by category, with the number of labels each rests on.
- Alpha by rater pair or with each rater left out, to find one reader who differs.
- Alpha by language variety.
- The guideline version, the raters and the sample it was measured on.

#### [day1#checkpoint-3] Which agreement figure do you trust?

*Checkpoint*

**Question:** Two raters label whether a complaint is WARRANTY. They agree on 96% of 300 complaints; each says WARRANTY about 3% of the time. What is the best next step?

- A. Accept: 96% agreement is excellent
- B. Compute a chance-corrected figure and count the WARRANTY labels it rests on
- C. Add a third rater and recompute percent agreement
- D. Merge WARRANTY into DEFECT to raise agreement

#### [day1#lab-1-3] Kappa and alpha on the pilot

Lab 1.3 · 25 min

Compute percent agreement, kappa by pair and Krippendorff's alpha on 300 pilot complaints labelled by three raters, by category and language variety, with bootstrap intervals.

[D1_3_compute_kappa_alpha.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D1_3_compute_kappa_alpha.ipynb)

- [ ] Percent agreement, and why it flatters (4 min)
- [ ] Cohen's kappa for each pair of raters (6 min)
- [ ] Krippendorff's alpha from the coincidence matrix (7 min)
- [ ] By category and by variety, with intervals (8 min)
- [ ] ✱ Stretch: Alpha when one rater skipped twenty complaints

### Session 4: Adjudication and revision

#### [day1#s4] Adjudication and revision

*Session 4*

- Adjudicate disagreements with a decision and a reason code
- Tie every guideline revision to a measured disagreement in a change log
- Measure whether the revision raised agreement in the next round

#### [day1#majority-is-not-adjudication] A majority of three can be wrong in the same way

*Three labels, one decision*

**8 of 28** majorities in the 30 disagreements that the adjudicator overturned

- Two raters who share a misreading outvote the one who read the rule.
- A vote has no reason attached, so it teaches the guideline nothing.
- Adjudication applies the guideline, and records why.

#### [day1#adjudication-methods] Choose the adjudication method by the kind of disagreement

*Ways to decide*

| Method | Good for | Risk |
| --- | --- | --- |
| Majority vote | random slips, many raters | shared misreadings win |
| Expert adjudicator | systematic splits, a pilot | one person's reading becomes the rule |
| Discussion to consensus | new edge cases | the loudest voice wins |
| Keep the disagreement | genuinely ambiguous items | analysts must handle soft labels |

#### [day1#reason-codes] Every decision gets a reason code

*Lab 1.4*

- **RULE_ORDER.** Two categories applied; the order decided. The rule may need an example.
- **MISREAD.** A rater missed a fact, often in dialect or mixed text. The language notes may need a line.
- **DEFINITION.** The definition did not cover the case. The guideline must change.

Counted over the 30 disagreements, the codes say which part of the guideline to revise.

#### [day1#adjudicate-from-facts] Agree on the facts, and the rules give the label

*One disagreement, decided*

- complaint: C103462, Gulf dialect: the wardrobe broke after 5 days; "I asked for my money and they refused"
- raters: R1 DEFECT · R2 DEFECT · R3 REFUND
- facts: `faulty=1 asked_refund=1 refund_refused=1`
- rule: rule 2 applies before rule 3
- decision: REFUND · reason RULE_ORDER · the majority overturned

#### [day1#change-log-with-evidence] Each revision cites the disagreement that caused it

*Guideline v1.1*

| Change | Evidence from the 30 |
| --- | --- |
| Rule 2 gets the example "broken and refund refused is REFUND" | DEFECT and REFUND split 5 times |
| DEFECT's excludes name WARRANTY first, with the Gulf wording | WARRANTY and DEFECT split 5 times; R3 said DEFECT 6 times |
| Rule 5: read the charge against the displayed price first | AD and PRICE split 3 times |
| Language notes: code-switched "refund", "no refund policy" | 8 MISREAD decisions |

#### [day1#round-two-agreement] Round 2 under v1.1: alpha from 0.594 to 0.789

*Did the revision work?*

| Alpha | Round 1 | Round 2 |
| --- | --- | --- |
| All categories | 0.594 | 0.789 |
| WARRANTY | 0.164 | 0.680 |
| REFUND | 0.512 | 0.791 |
| Gulf dialect | 0.470 | 0.782 |
| Mixed | 0.340 | 0.743 |

Round 2 interval for all categories: 0.744 to 0.825. Mixed text stays the weakest variety.

#### [day1#checkpoint-4] Which change-log entry would you accept?

*Checkpoint*

**Question:** Khulood reviews four proposed entries for guideline v1.1. Which one meets the standard of this course?

- A. "Definitions clarified throughout for consistency"
- B. "REFUND and DEFECT split 5 of 30: raters to take more care"
- C. "Rule 5 restated because AD seems clearer than PRICE"
- D. "Rule 2 example added: broken and refund refused is REFUND (split 5 of 30)"

#### [day1#lab-1-4] Adjudicate 30, revise, measure again

Lab 1.4 · 25 min

Adjudicate 30 pilot disagreements with reason codes, revise the guideline to v1.1 with a change log tied to the counts, and compare alpha in round 1 and round 2.

[D1_4_adjudicate_30_disagreements.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D1_4_adjudicate_30_disagreements.ipynb)

- [ ] Sort the 30 disagreements by category pair (5 min)
- [ ] Adjudicate: a decision and a reason code each (8 min)
- [ ] Guideline v1.1: a change log tied to the counts (7 min)
- [ ] Round 2: did agreement rise, and where (5 min)
- [ ] ✱ Stretch: How often was the majority of three raters wrong?

#### [day1#wrap-up] Three things to keep

*Day 1 · wrap-up*

- **Labels are measurements.** A construct, an instrument and an error. Measure the error twice before trusting a figure.
- **Correct for chance.** Report alpha with an interval, by category and by language, not percent agreement alone.
- **Revise with evidence.** Adjudicate with reasons; tie each change to a count; measure again.

#### [day1#next] Day 2: Golden sets and labelling operations

*Next*

Keep guideline v1.1 and your agreement report. Tomorrow: a golden set, gold checks over six raters, a drifting rater, and the cost of each labelling design.
