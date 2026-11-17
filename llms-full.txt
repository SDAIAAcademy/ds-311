---
course: "Data Quality, Labelling and Pipelines for Analysis"
code: "DS-311"
version: "2027.1.0"
scope: "course"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-311/"
---

# Data Quality, Labelling and Pipelines for Analysis

Build the labels, rules, contract and gated pipeline an analysis depends on, and trace a figure that changed

Participants build the data an analysis depends on for Bayyin Consumer Protection Office, a fictional regulator holding 30,000 synthetic complaint records in Arabic and English. They write a labelling guideline, pilot it, measure agreement and adjudicate, run golden-question checks and review queues across a rater team, turn analysts' requirements into quality rules and a data contract, and package the preparation as a reproducible pipeline that stops on those rules. Measuring model-made labels is DS-306; platform-scale data engineering is AE-306.

- **Audience:** Practitioners. Data scientists and analysts who have completed the level 200 set or can show equivalent work: an analysis they framed, carried out and explained to a stakeholder.
- **Prerequisites:** DS-202 Data Acquisition, Preparation and Quality; FN-102 Command Line, Git and Reproducible Projects; Writes Python functions and SQL queries; Uses Git and a lock-file environment; Setup: a laptop CPU with uv, or Google Colab. Nothing downloads a model; one lab calls a free hosted model and runs without a key on a stand-in. Run 00_setup_check before Day 1; see labs/README.md.
- **Case study:** Bayyin Consumer Protection Office: Bayyin is a fictional consumer protection regulator with 30,000 synthetic complaints in Modern Standard Arabic, Gulf dialect, English and code-switched text, four source tables and a monthly complaint rate per 100,000 residents that its analysts publish. Participants write and pilot a six-category labelling guideline, measure and adjudicate agreement, run gold checks, review queues and drift monitoring over six raters, turn requirements into severity rules and an open-standard contract, and package the preparation as a pipeline that quarantines, blocks and leaves lineage. All data is synthetic and generated with a fixed seed.

## Outcomes

- LO1 (Applied): Draft a labelling guideline with definitions, decision rules and edge cases, and revise it after a pilot, given 300 synthetic complaints labelled by three raters
- LO2 (Applied): Compute chance-corrected agreement by category and rater, and adjudicate the disagreements, given two rounds of pilot labels
- LO3 (Applied): Configure a labelling workflow with golden-question checks, review queues and rater-drift monitoring, given a simulated round of 2,000 items from six raters, one of whom drifts
- LO4 (Applied): Implement quality rules with thresholds and severities, and a data contract for the prepared table, given four source tables with seeded defects
- LO5 (Performance): Build a reproducible preparation pipeline from raw extracts to an analysis-ready table that stops on a blocking rule, given a repository with continuous integration
- LO6 (Performance): Diagnose why an analytical figure changed after a data refresh and decide on the correction, given two runs, their lineage records and a stakeholder asking which figure is right

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

## Day 2: Golden sets and labelling operations

Run a rater team with gold questions, queues and a cost

#### [day2#title] Golden sets and labelling operations

*SDAIA Academy · Data Quality, Labelling and Pipelines for Analysis*

Day 2: Run a rater team with gold questions, queues and a cost

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-311

#### [day2#review-day1] Which number goes in the agreement report?

*Review of Day 1*

**Question:** Round 2 of the pilot gives alpha 0.789 overall, with an interval from 0.744 to 0.825, and 0.743 for mixed text from 15 complaints. Which sentence belongs in the report?

- A. "Agreement is 0.789."
- B. "Agreement is 0.789 (0.744 to 0.825), so every variety is reliable."
- C. "Agreement is 0.789 (0.744 to 0.825); mixed text is lowest, on only 15 complaints."
- D. "Mixed text is excluded because 15 complaints are too few."

#### [day2#agenda] Golden sets and labelling operations

*Today*

- **Session 1 · Sampling a golden set**: A golden set stratified on what is known before labelling, with floors for rare categories and dialects
- **Session 2 · Gold questions and review queues**: Gold questions mixed into the work, a pass rule with a minimum count, and routing rules that send each item where it belongs
- **Session 3 · Rater drift and workload**: Each rater against their own baseline, drift told apart from steady low accuracy, and workload against the guideline's limits
- **Session 4 · Cost and model pre-labels**: Cost per accepted label across three designs, with personal data masked and classified before any model call

### Session 1: Sampling a golden set

#### [day2#s1] Sampling a golden set

*Session 1*

- Explain why a simple random sample misses rare categories and dialects
- Stratify on fields known before labelling, with a floor per stratum
- Weight a stratified sample back to the population

#### [day2#what-gold-is-for] Gold questions measure each rater against a known answer

*A golden set*

- **What it is.** Complaints labelled by experts and adjudicated: the expected answer is known.
- **How it is used.** Mixed into each rater's work, unmarked. Accuracy on them estimates accuracy on the rest.
- **What it must cover.** Every category and every language variety, including the rare ones a rater might miss.

> **What goes wrong.** A golden set of easy, common complaints scores everyone highly and tests nothing.

#### [day2#random-sample-misses] A random sample holds four WARRANTY complaints

*Lab 2.1, a simple random sample of 240*

- **4** WARRANTY complaints of 240
- **18** mixed Arabic and English
- **2** WARRANTY in mixed text

A rater who misses every WARRANTY complaint still scores above 98% on this gold set.

#### [day2#stratify-on-known-fields] Stratify on what is known before labelling

*What you can stratify on*

- The **true category** is what labelling produces: not available yet.
- The **language variety** is known from language detection.
- A **pre-label** from keywords or a model is known, and right about four times in five.
- 24 strata: four varieties times six pre-labels.

- **The smallest strata.** Mixed text pre-labelled WARRANTY, English pre-labelled WARRANTY: the ones that matter most for gold.

#### [day2#floor-per-stratum] A floor per stratum, the rest in proportion

*How many from each stratum*

1. **1 · Floor** min(6, stratum size) each
2. **2 · Share the rest** in proportion to what is left
3. **3 · Round** so the total is exactly 240
4. **4 · Draw** with a fixed seed

> **The trade.** A floor costs precision in the large strata and buys enough rare cases to test raters on them.

#### [day2#stratified-coverage] The stratified set holds seven times the WARRANTY complaints

*Lab 2.1, after expert labelling*

| 240 complaints | WARRANTY | Mixed text | WARRANTY in mixed |
| --- | --- | --- | --- |
| Simple random sample | 4 | 18 | 2 |
| Stratified, floor of six | 29 | 42 | 7 |

Coverage is counted on the experts' labels, not on the pre-labels the strata used.

#### [day2#weight-back] An oversampled set must be weighted before it estimates shares

*Using gold for estimates*

| Item | Value |
| --- | --- |
| WARRANTY, unweighted | 12.1% |
| WARRANTY, weighted | 3.4% |
| WARRANTY, whole corpus | 2.5% |

Each drawn complaint stands for Nh / nh complaints of its stratum.

#### [day2#hidden-gold] Raters learn gold questions they see too often

*Gold that stays useful*

- Draw gold from the same mix of varieties and lengths as the work, so it cannot be spotted.
- Rotate: each gold item appears to a rater at most a few times.
- Keep a hidden half for audits nobody has seen.
- Version the golden set with the guideline: a changed rule changes some gold answers.

#### [day2#checkpoint-1] How do you get enough rare cases into the golden set?

*Checkpoint*

**Question:** Bayyin must build a 240-complaint golden set that tests raters on WARRANTY, about 2.5% of complaints. No complaint is labelled yet. What do you stratify on?

- A. The true category of each complaint
- B. Nothing: draw a random sample of 480 instead
- C. The channel the complaint came through
- D. The language variety and a pre-label, with a floor per stratum

#### [day2#lab-2-1] A stratified golden set

Lab 2.1 · 25 min

Draw a 240-complaint golden set stratified by language variety and pre-label with a floor per stratum, compare its coverage with a random sample, and weight it back to the population.

[D2_1_draw_stratified_golden.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D2_1_draw_stratified_golden.ipynb)

- [ ] What a random sample of 240 misses (4 min)
- [ ] Strata from what is known before labelling (6 min)
- [ ] Allocate with a floor per stratum, and draw (8 min)
- [ ] Coverage under expert labels, and the weights (7 min)
- [ ] ✱ Stretch: Keep half of the gold hidden for later audits

### Session 2: Gold questions and review queues

#### [day2#s2] Gold questions and review queues

*Session 2*

- Estimate each rater's gold accuracy with an interval
- Set a pass rule that needs a minimum number of gold answers
- Route items to acceptance, adjudication or a restricted queue

#### [day2#operations-round] Ten days, six raters, eight gold questions each a day

*The operations round*

- **2,015** work items
- **2,986** labels in all
- **480** gold answers
- **1 in 4** items labelled twice

Distressing complaints go only to the two raters approved for them, R2 and R4.

#### [day2#gold-accuracy-interval] Three raters fall below the line, one of them by a hair

*Lab 2.2, 80 gold answers per rater*

| Rater | Right | Accuracy | 95% interval |
| --- | --- | --- | --- |
| R1 | 76 | 0.950 | 0.878 to 0.980 |
| R2 | 75 | 0.938 | 0.862 to 0.973 |
| R3 | 71 | 0.888 | 0.7998 to 0.940 |
| R4 | 72 | 0.900 | 0.815 to 0.948 |
| R5 | 57 | 0.712 | 0.605 to 0.800 |
| R6 | 58 | 0.725 | 0.619 to 0.811 |

#### [day2#pass-rule-minimum] Judge the lower end of the interval, after a minimum count

*Turning scores into a decision*

```python
# file: Lab 2.2
MIN_GOLD, LOWER = 30, 0.80

def status(row):
    if row.n < MIN_GOLD:
        return "too few"
    return "pass" if row.lo >= LOWER else "watch"
```

- **Why a minimum.** 9 of 9 right has an interval reaching down to about 0.70.
- **Why the lower bound.** A rater passes when we are fairly sure they are good enough, not when they might be.

#### [day2#routing-rules] Every item goes to exactly one queue

*Review queues*

1. **Distressing?** restricted queue: approved raters only
2. **Two labels that disagree?** adjudication
3. **One label from a rater on watch?** re-label
4. **Otherwise** accept

#### [day2#queue-sizes] Almost half of the round needs a second look

*Lab 2.2, 2,015 work items*

| Item | Value |
| --- | --- |
| Accept | 1,081 |
| Re-label | 731 |
| Adjudicate | 139 |
| Restricted | 64 |

Tomorrow's work: 3.5 adjudicator hours, 8.3 hours of re-labelling, 3.6 hours in the restricted queue.

#### [day2#restricted-compliance] The restricted queue is audited, not assumed

*Checking the wellbeing rule*

**0** restricted items labelled by a rater who is not approved

- The check reads the labels, not the routing settings.
- A zero is evidence; an unchecked setting is a hope.
- The time limit is checked separately, per rater and day, in Session 3.

#### [day2#checkpoint-2] Does this rater pass?

*Checkpoint*

**Question:** A new rater has answered 12 gold questions and got all 12 right. Bayyin's rule needs 30 gold answers and a lower bound of at least 0.80. What is their status?

- A. Pass: 100% accuracy
- B. Too few: keep giving gold questions until 30
- C. Watch: the interval is too wide
- D. Re-label all their work

#### [day2#lab-2-2] Gold checks and routing

Lab 2.2 · 25 min

Score six raters on the gold questions of a 2,000-item round with Wilson intervals, set a pass rule, and route every item to acceptance, adjudication or the restricted queue.

[D2_2_set_gold_question.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D2_2_set_gold_question.ipynb)

- [ ] Gold accuracy per rater, with an interval (6 min)
- [ ] A pass rule with a minimum count (5 min)
- [ ] Routing: accept, adjudicate, restricted queue (8 min)
- [ ] Queue sizes and adjudicator hours (6 min)
- [ ] ✱ Stretch: Gold questions a rater cannot spot

### Session 3: Rater drift and workload

#### [day2#s3] Rater drift and workload

*Session 3*

- Track gold accuracy per rater over time
- Flag drift against a rater's own baseline, not the team average
- Check workload and distressing-content time against the guideline

#### [day2#drift-versus-steady] The same average can come from two different problems

*Two raters far below the line*

- **Steadily low.** Always below the team. Needs coaching and double labelling; past work is as good as it ever was.
- **Drift.** Was good, then changed. Needs a conversation about what changed, and recent work re-checked.

R5 ends at 0.712 and R6 at 0.725 over ten days. Only the daily picture tells them apart.

#### [day2#daily-accuracy] R5 falls from day 6; R6 was low from the start

*Lab 2.3, gold accuracy by day (eight answers a day)*

| Rater | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | 1.00 | 0.88 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.88 | 0.88 | 0.88 |
| R5 | 1.00 | 1.00 | 1.00 | 1.00 | 0.88 | 0.50 | 0.62 | 0.50 | 0.38 | 0.25 |
| R6 | 0.38 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | 0.88 |

Eight gold answers a day make each cell coarse: one answer moves it by 0.125.

#### [day2#own-baseline-rule] Compare each rater with their own first days

*A drift rule*

1. Baseline: days 1 to 5, 40 gold answers.
2. Recent: days 8 to 10, 24 gold answers.
3. One-sided two-proportion test on the drop.
4. Flag when the drop is at least 0.10 and z is at least 2.

| Rater | Base | Recent | z |
| --- | --- | --- | --- |
| R5 | 0.975 | 0.375 | 5.37 |
| R4 | 0.925 | 0.792 | 1.56 |
| R6 | 0.675 | 0.792 | -1.00 |

#### [day2#team-rule-fails] A team rule flags who is lowest, not who changed

*Why not a team-average rule?*

| Rater | Ten-day accuracy | Team rule | Own-baseline rule | Diagnosis |
| --- | --- | --- | --- | --- |
| R5 | 0.712 | flagged | flagged | **drift** |
| R6 | 0.725 | flagged | not flagged | **steady-low** |

> **The response follows the diagnosis.** R5's 211 work labels since day 6 go back for re-checking; R6 stays on double labelling and gets coaching.

#### [day2#what-r5-confuses] After day 6, R5 calls defects and deliveries refunds

*Lab 2.3 stretch*

| Gold label, days 6 to 10 | R5 said REFUND | R5 right |
| --- | --- | --- |
| DEFECT | 8 | 2 |
| DELIVERY | 7 | 1 |
| REFUND | 6 | 6 |

A pattern like this points at a reading of rule 2 that spread too far: "any mention of money is REFUND".

#### [day2#workload-and-limits] One rater went past the distressing-content limit

*Workload against the guideline*

**69 min** R4 on day 7, against a limit of 60

| Item | Value |
| --- | --- |
| R6 | 150 an hour |
| R1 | 93 |
| R5 | 89 |
| R2 | 56 |

R6 labels almost three times as fast as R2 and is the least accurate: speed is a quality signal too.

#### [day2#checkpoint-3] Which response fits R5?

*Checkpoint*

**Question:** R5 scored 0.975 on gold for five days and 0.375 for the last three. R6 has scored about 0.72 throughout. What should happen to R5's work?

- A. Put R5 on double labelling from now on, like R6
- B. Re-label everything R5 has ever labelled
- C. Re-check R5's work since the drift began, and find out what changed
- D. Nothing: R5's ten-day average is close to R6's

#### [day2#lab-2-3] Find the drifting rater

Lab 2.3 · 25 min

Track gold accuracy per rater over ten days, flag the rater who drifts against their own baseline, tell drift from steady low accuracy, and check distressing-content minutes against the guideline.

[D2_3_find_drifting_rater.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D2_3_find_drifting_rater.ipynb)

- [ ] Gold accuracy by rater and day (5 min)
- [ ] A drift rule against each rater's own baseline (8 min)
- [ ] Drift or steadily low? (5 min)
- [ ] Workload and distressing-content minutes (7 min)
- [ ] ✱ Stretch: Which categories does the drifting rater now confuse?

### Session 4: Cost and model pre-labels

#### [day2#s4] Cost and model pre-labels

*Session 4*

- Compute cost per accepted label for a labelling design
- Mask personal data and classify what may leave the organisation before a model call
- Compare double, audited single and model-assisted labelling on cost and error

#### [day2#cost-per-accepted-label] Cost per accepted label counts every check, not only the first pass

*What a label costs*

- **Rater time.** Seconds per label times the hourly rate, for every label made.
- **Review time.** Audits and adjudication: 90 seconds of a more senior person.
- **Divide by accepted.** Only labels that passed the design's own checks count.

> **What goes wrong.** A cheap first pass whose error is too high is not cheap: the analysts pay for it later in a wrong figure.

#### [day2#mask-and-classify] Mask, then classify: only what is safe leaves the office

*Before any model call*

1. **Raw text** Restricted: names, phones, IDs, IBANs
2. **Mask** identifiers replaced by tags
3. **Classify** anything that still looks like an identifier stays Restricted
4. **Send** only what the owner cleared

SDAIA's Generative AI Guidelines for Government tell staff not to enter data classified Restricted or higher into generative AI tools.

#### [day2#arabic-digits-leak] A pattern for Latin digits misses numbers written in Arabic-Indic digits

*Lab 2.4*

```python
# file: mask(text)
t = text.translate(B.TO_LATIN)   # ٠١٢ → 012
for name in ["IBAN", "EMAIL", "PHONE",
             "NATIONAL_ID"]:
    t = re.sub(B.PII_PATTERNS[name],
               f"[{name}]", t)
```

**19 of 40** complaints still carry an identifier after a naive phone pattern

- After full masking, 40 of 40 are classified safe to send.

#### [day2#prelabel-call] One chat-completions call per masked complaint

*Fahis, the pre-labelling step*

Prompt for System message:

```text
You label consumer complaints for a consumer protection office. Reply with exactly one code: REFUND, DEFECT, DELIVERY, PRICE, AD or WARRANTY. Rules in order: warranty repair refused is WARRANTY; refund asked and refused is REFUND; …
```

- **A free hosted model.** An open-weight model through OpenRouter's free tier; any OpenAI-style endpoint works.
- **Without a key.** A scripted stand-in answers, and the notebook says so. Its labels are keyword rules, not a model's.

#### [day2#three-designs-cost] The cheapest design is also the least accurate

*Lab 2.4, a trial on 300 gold complaints*

| Design | SAR per accepted label | Error against gold | Adjudicated |
| --- | --- | --- | --- |
| Double labelling | 1.94 | 0.3% | 51 |
| Audited single (15% audit) | 0.93 | 5.0% | 5 |
| Model-assisted, every pre-label checked | 0.37 | 10.0% | 0 |

With a limit of 5% wrong labels, audited single labelling is the cheapest design that qualifies.

#### [day2#anchoring] People confirm a wrong pre-label more often than they should

*Why model-assisted errs*

**28%** of 60 wrong pre-labels confirmed by the person checking

- Confirming is fast; disagreeing takes thought.
- Hide the pre-label on a sample of items to measure the effect.
- Never accept a pre-label unseen: the entry's AI policy and the office's.

#### [day2#qc-report] The quality-control report in five lines

*The evidence for LO3*

1. Gold accuracy per rater with intervals; R3 (by a hair), R5 and R6 on watch.
2. R5 drifted from day 6; 211 work labels re-checked. R6 steadily low: coaching and double labelling.
3. Queues: 1,081 accepted, 731 re-label, 139 adjudication, 64 restricted; 15 hours of review.
4. One breach of the distressing-content limit (R4, day 7, 69 minutes); routing cap added.
5. Audited single labelling at SAR 0.93 per accepted label and 5.0% error.

#### [day2#checkpoint-4] Which design would you choose?

*Checkpoint*

**Question:** Analysts accept at most 5% wrong labels. Double labelling costs SAR 1.94 at 0.3% error; audited single SAR 0.93 at 5.0%; model-assisted SAR 0.37 at 10.0%. Which design, and why?

- A. Model-assisted: it is the cheapest
- B. Double labelling: it has the fewest errors
- C. A mix of all three in equal shares
- D. Audited single: the cheapest design within the error limit

#### [day2#lab-2-4] Cost per accepted label

Lab 2.4 · 25 min

Mask and classify complaints before any model call, pre-label the masked ones through a chat-completions endpoint, and compare cost per accepted label and error across double, audited single and model-assisted labelling.

[D2_4_compare_cost_per.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D2_4_compare_cost_per.ipynb)

- [ ] Mask personal data; classify what may leave (7 min)
- [ ] Pre-label masked complaints through the endpoint (5 min)
- [ ] Cost and error of three designs (9 min)
- [ ] Choose a design, and the condition that would change it (4 min)
- [ ] ✱ Stretch: Anchoring: how often do people confirm a wrong pre-label?

#### [day2#wrap-up] Three things to keep

*Day 2 · wrap-up*

- **Gold that covers the rare.** Stratify on what you know before labelling, with a floor; weight before you estimate.
- **Own baseline for drift.** A team rule finds the lowest; an own-baseline rule finds who changed.
- **Mask, classify, then count cost.** Nothing Restricted leaves; cost is compared within the error limit.

#### [day2#next] Day 3: Rules and contracts

*Next*

Four source tables with seeded defects. The first lab is AI-off: read a profile and propose rules on your own.

## Day 3: Rules and contracts

Turn analysts' requirements into rules and a contract

#### [day3#title] Rules and contracts

*SDAIA Academy · Data Quality, Labelling and Pipelines for Analysis*

Day 3: Turn analysts' requirements into rules and a contract

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-311

#### [day3#review-day2] Who needs which response?

*Review of Day 2*

**Question:** Over ten days R5 and R6 both average about 0.72 on gold. R5 scored 0.975 in the first five days and 0.375 in the last three; R6 stayed between 0.68 and 0.79. What do you do?

- A. Coach both raters the same way
- B. Re-check R5's recent labels; coach R6 and double-label its work
- C. Re-check R6's recent labels; leave R5, whose average is the same
- D. Wait for more gold answers before doing anything

#### [day3#agenda] Rules and contracts

*Today*

- **Session 1 · Profiling to rules**: A profile of each source table, read against the six quality dimensions, becomes rules with owners and thresholds
- **Session 2 · Rules with severity**: Warn, quarantine or block: a rule as a query that returns failing rows, judged on seeded defects and on clean data
- **Session 3 · Duplicates and merchant matching**: Exact and near duplicates, and merchant names matched across Arabic and Latin spellings with measured precision
- **Session 4 · A data contract**: A contract in an open standard that the producer and the consumer of the prepared table both check

### Session 1: Profiling to rules

#### [day3#s1] Profiling to rules

*Session 1*

- Profile tables for completeness, uniqueness, validity, consistency, accuracy and timeliness
- Read anomalies from a profile without help
- Write a rule with an owner, a dimension, a threshold and a business reason

#### [day3#four-tables] Four tables feed one published rate

*What Bayyin prepares every month*

- **Complaints.** The portal extract of 5 September: 30,300 rows, one per complaint, with its category from the labels.
- **Merchants.** The registry: 153 rows, Arabic and English names, a commercial registration number.
- **Regions.** Thirteen regions with their populations: the denominator of the rate.
- **Case actions.** 30,148 actions taken by officers: warnings, referrals, refunds.

> **What goes wrong.** Each table can be correct on its own and the join still wrong: a missing region drops a complaint from the rate silently.

#### [day3#six-dimensions] Six dimensions organise what a profile can show

*The NDMO Data Quality domain*

| Dimension | The question | In Bayyin's extract |
| --- | --- | --- |
| Completeness | Is the value there? | Region empty on 414 complaints |
| Uniqueness | Is each thing recorded once? | 60 complaint ids appear twice |
| Validity | Is the value allowed? | Category "defect" and "C7"; region R99 |
| Consistency | Do related values agree? | 85 closed before they were received |
| Accuracy | Is the value true? | Amounts of SAR 694,783 |
| Timeliness | Is it recent enough? | Newest complaint against the extract date |

#### [day3#profile-as-text] Profile the values as they arrived, loaded as text

*Lab 3.1, before any rule*

```sql
-- file: profile(table)
SELECT count(*) FILTER (WHERE c IS NULL
                         OR trim(c) = '') AS empty,
       count(DISTINCT c)  AS distinct_values,
       min(c), max(c), mode(c),
       min(TRY_CAST(c AS DOUBLE)),
       max(TRY_CAST(c AS DOUBLE))
FROM complaints
```

- **Why text.** A typed load turns "warranty" or "2027-06-25" into an error or a NULL before anyone sees it.
- **AI-off.** Lab 3.1 is done without an assistant: reading a profile is the skill.

#### [day3#profile-findings] The profile points at the anomalies; one query confirms each

*Lab 3.1, read from the profile*

| What the profile shows | Confirmed by | Rows |
| --- | --- | --- |
| 30,300 rows, 30,240 distinct ids | count minus count distinct | 60 |
| 13 category codes for six categories | codes outside the six | 170 |
| Maximum amount SAR 694,783 | amounts above SAR 50,000 | 619 |
| Latest received date 2027-06-25 | after the extract date | 12 |
| 14 region codes for 13 regions; 414 empty | not in the regions table | 600 |
| Actions for 22,676 complaint ids | action without a complaint | 150 |

#### [day3#halala-batch] August's app batch arrived in halalas

*The anomaly the maximum hides*

| Item | Value |
| --- | --- |
| App, June | SAR 545 |
| App, July | SAR 694 |
| App, August | SAR 54,706 |
| Web, August | SAR 530 |

Median amount by month and channel. Multiplied by 100, only 619 of the 1,195 amounts pass SAR 50,000.

#### [day3#rule-anatomy] A rule names its owner, dimension, attributes and threshold

*What a rule must state*

```python
# file: pipeline/rules.py
dict(id="C01", dimension="completeness",
     owner="Hatoon Al-Furaih",
     table="complaints",
     description="Every complaint has a region: "
                 "the rate is published by region",
     attributes=["region_code"],
     severity="quarantine", max_rate=0.03,
     sql="SELECT rid FROM complaints WHERE "
         "region_code IS NULL OR trim(region_code) = ''")
```

- **Owner.** Who accepts the threshold and answers when the rule fires.
- **Business description.** Why the figure needs it, in the user's words.
- **Threshold.** The share of failing rows the owner accepts.

#### [day3#checkpoint-1] Is the maximum enough?

*Checkpoint*

**Question:** The profile shows a maximum amount of SAR 694,783. Abdulelah proposes one rule: "no amount above SAR 50,000". August's app batch was sent in halalas. What does his rule miss?

- A. The halala amounts that stayed under SAR 50,000; a rule on the batch's median catches them
- B. Nothing: every halala amount is above SAR 50,000
- C. The duplicated complaints of August
- D. Only amounts between SAR 40,000 and 50,000; lower the limit to 40,000

#### [day3#lab-3-1] Profile four tables, propose rules

Lab 3.1 · 25 min

Profile four source tables in DuckDB without AI help, find the anomalies, and propose rules with a dimension, an owner, a threshold and a reason.

[D3_1_profile_four_source.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D3_1_profile_four_source.ipynb)

- [ ] Profile each table in DuckDB (8 min)
- [ ] Five anomalies from the profile (7 min)
- [ ] Rules with dimension, owner and threshold (10 min)
- [ ] ✱ Stretch: Timeliness: how old is the newest complaint in each extract?

### Session 2: Rules with severity

#### [day3#s2] Rules with severity

*Session 2*

- Write a rule as a query that returns the failing rows
- Give each rule a severity: warn, quarantine or block
- Show that the rules catch each seeded defect and stay quiet on clean data

#### [day3#rule-as-query] A rule is a query that returns the failing rows

*One shape for every rule*

```sql
-- file: K01
SELECT rid FROM complaints
WHERE coalesce(closed_date, '') <> ''
  AND TRY_CAST(closed_date AS DATE)
    < TRY_CAST(received_date AS DATE)
```

- The same query **counts** failures, **lists** them and **moves** them to quarantine.
- Every table gets a row id, `rid`, so a failing row can be named.
- Rules run on text: a bad value fails the rule, not the load.

#### [day3#severity-ladder] Warn, quarantine or block

*What happens when a rule fails*

1. **Warn** log it; the run goes on
2. **Quarantine** set the failing rows aside with the rule id; stop above the threshold
3. **Block** stop before anything is published

> **Choosing.** Quarantine when the remaining rows are still right; block when the error could be in rows that look fine.

#### [day3#rule-results] Two accuracy rules stop the run; the rest quarantine or log

*Lab 3.2, the seeded extract*

| Rule | Dimension | Owner | Failing | Threshold | Action |
| --- | --- | --- | --- | --- | --- |
| U01 one row per id | uniqueness | Abdulelah | 60 | 0.5% | quarantined |
| C01 region present | completeness | Hatoon | 414 | 3% | quarantined |
| V02 category valid | validity | Khulood | 170 | 1% | quarantined |
| K01 closed after received | consistency | Abdulelah | 85 | 0.5% | quarantined |
| A01 amount ≤ SAR 50,000 | accuracy | Hatoon | 619 | 0.1% | stop |
| A02 monthly median by channel | accuracy | Hatoon | 1,195 | 0.1% | stop |
| U02 one entry per CR number | uniqueness | Abdulelah | 3 | 0 | logged |

#### [day3#judge-both-ways] Catch every seeded defect, and stay quiet on clean data

*How a rule set is judged*

- **On the seeded extract.** Eight listed defects, each caught in full by the rule meant for it: 60 duplicates, 600 regions, 170 codes, 85 dates out of order, 1,195 halala amounts, 12 future dates, 150 orphan actions, 3 registry duplicates.
- **On the clean extract.** The same eleven rules on the same month without defects: no rule fails a single row.

> **What goes wrong.** A rule that fires on good data trains people to ignore it, and then to switch it off.

#### [day3#pandera] A validation library expresses the same rules as a schema

*The same checks in a framework*

```python
# file: Pandera, stretch of Lab 3.2
pa.DataFrameSchema({
  "complaint_id": pa.Column(str, unique=True),
  "category_code": pa.Column(str,
      pa.Check.isin(SIX)),
  "amount_sar": pa.Column(float,
      pa.Check.le(50000), nullable=True),
})
```

- Finds the same failures: 120 rows in duplicated ids, 170 codes, 619 amounts.
- Keeps owners, severities and thresholds outside the schema: you still need them.
- The SQL rules run where the data is; the schema runs where the DataFrame is.

#### [day3#checkpoint-2] What should C01 do?

*Checkpoint*

**Question:** C01 (region present) is a quarantine rule with a 3% threshold. This month 414 of 30,300 complaints, 1.4%, have no region. What happens to the run?

- A. The run stops before publishing
- B. The rows are published with an empty region and a warning
- C. The 414 rows go to quarantine with C01; the run goes on
- D. The rows are given the most common region and published

#### [day3#lab-3-2] Warning and blocking rules

Lab 3.2 · 25 min

Implement the rule set as SQL with thresholds and severities, catch every seeded defect in the four tables, and show no false alarm on the clean tables.

[D3_2_implement_warning_blocking.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D3_2_implement_warning_blocking.ipynb)

- [ ] A rule as a query that returns failing rows (5 min)
- [ ] The rule set with thresholds and severities (9 min)
- [ ] Every seeded defect caught (6 min)
- [ ] No alarm on the clean tables (5 min)
- [ ] ✱ Stretch: Three of the rules again in Pandera

### Session 3: Duplicates and merchant matching

#### [day3#s3] Duplicates and merchant matching

*Session 3*

- Tell exact duplicates from resubmissions
- Normalise Arabic and Latin names and compare them through a transliteration key
- Choose a match threshold from precision and recall on labelled pairs

#### [day3#exact-vs-near] An exact duplicate is an export fault; a resubmission is a person

*Duplicates*

- **Exact duplicates: 60.** The same complaint id twice. The portal's export wrote a row again. Rule U01 quarantines the second copy.
- **Resubmissions: 240.** A new id, the same customer, merchant and product, a day later: the complainant tried again. Each row is valid.

> **What goes wrong.** A key too wide merges real repeat complaints; a key too narrow counts one problem twice. The choice of key changes the rate.

#### [day3#merchant-spellings] One merchant, written a dozen ways

*The merchant on a complaint*

| As typed by the complainant | Registry |
| --- | --- |
| مؤسسة النور للإلكترونيات المحدودة | M1001 |
| AL-NOOR ELECTRONICS CO. | M1001 |
| Alnoor Elec. | M1001 |
| النور Electronics | M1001 |
| شركة الفارسللأزياء المحدودة | M1130 |

600 raw names in the lab; 300 are labelled with the right registry id, or NONE.

#### [day3#transliteration-key] Normalise, then compare consonant skeletons

*Lab 3.3, comparing across scripts*

1. **1 · Normalise** unify أ إ آ, ة, ى; drop legal forms and the article
2. **2 · Sector** stems in both scripts: «لكترون», "elec"
3. **3 · Skeleton** consonants in Latin letters
4. **4 · Key** "nr|electronics"

«النور للإلكترونيات» and "Al-Noor Electronics" both give `nr|electronics`. The Arabic and English names agree on the key for all 150 merchants.

#### [day3#precision-first] Choose the threshold by precision first

*Lab 3.3, 300 labelled names*

| Threshold | Matched | Precision | Recall |
| --- | --- | --- | --- |
| 60 | 265 | 1.000 | 0.981 |
| 70 | 262 | 1.000 | 0.970 |
| 85 | 259 | 1.000 | 0.959 |
| 100 | 258 | 1.000 | 0.956 |

A tie between two merchants returns NONE. The five misses are typing errors in the sector word.

#### [day3#blocking] Blocking compares only names that could match

*Stretch of Lab 3.3*

**1,354** comparisons when blocked by sector and first letter, of 90,000

- Fine for 600 names; essential for 30,000 complaints a month.
- A block that is too strict hides true matches: check recall after blocking.
- Libraries for record linkage do the same with more care.

#### [day3#checkpoint-3] Should a bare name match?

*Checkpoint*

**Question:** A complainant writes only «النور», with no sector. Six registry merchants share that name: electronics, furniture, appliances, fashion, auto parts and jewellery. All score 100. What should the matcher return?

- A. The first of the six in the registry
- B. The one with the most complaints this year
- C. Raise the threshold until only one remains
- D. NONE, until someone checks the complaint text

#### [day3#lab-3-3] Merchant names across two scripts

Lab 3.3 · 25 min

Normalise 600 raw merchant names, match them to the registry across Arabic and Latin spellings, choose a threshold, and measure precision and recall on 300 labelled names.

[D3_3_match_merchant_names.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D3_3_match_merchant_names.ipynb)

- [ ] Normalise Arabic and Latin names (7 min)
- [ ] A transliteration key across scripts (6 min)
- [ ] Score, and choose a threshold (6 min)
- [ ] Precision and recall on 300 labelled names (6 min)
- [ ] ✱ Stretch: Blocking: compare fewer pairs

### Session 4: A data contract

#### [day3#s4] A data contract

*Session 4*

- Write a contract for a table in the Open Data Contract Standard
- Compile its quality clauses to SQL checks
- Tell a breaking schema change from a compatible one

#### [day3#producer-consumer] A contract writes down what the consumer relies on

*A data contract*

- **Producer: Abdulelah.** Runs the preparation pipeline and publishes `complaints_prepared`. Runs the contract before publishing.
- **Consumer: Hatoon.** Builds the monthly rate from it. Agrees the clauses; can run the contract on arrival.

> **What goes wrong.** Without a contract, a renamed column breaks the report on the morning it is due, and nobody knew it was relied on.

#### [day3#odcs-schema] The schema part: one property per column the consumer uses

*The Open Data Contract Standard, v3.2.0*

```yaml
# file: contract.odcs.yaml
apiVersion: v3.2.0
kind: DataContract
id: bayyin-complaints-prepared
version: 1.0.0
schema:
- name: complaints_prepared
  properties:
  - name: complaint_id
    logicalType: string
    physicalType: VARCHAR
    required: true
    primaryKey: true
  - name: region_code
    ...
```

- An open, vendor-neutral standard maintained by the Bitol project of the Linux Foundation.
- Ten properties for the ten columns of today's table.
- `description` says purpose, usage and limitations, in words.

#### [day3#quality-clauses] A small library of metrics, or a SQL query that returns a number

*Quality clauses*

```yaml
# file: contract.odcs.yaml
- name: category
  quality:
  - metric: invalidValues
    arguments:
      validValues: [REFUND, DEFECT, DELIVERY,
                    PRICE, AD, WARRANTY]
    mustBe: 0
- name: amount_sar
  quality:
  - type: sql
    query: SELECT count(*) FROM ${object}
           WHERE ${property} > 50000
    mustBe: 0
```

- Library metrics: nullValues, missingValues, invalidValues, duplicateValues, rowCount.
- Operators: mustBe, mustBeGreaterThan, mustBeLessThan and their kin.
- Six clauses in Lab 3.4, plus "required" on seven columns.

#### [day3#compile-to-sql] Every clause becomes one query and one comparison

*Lab 3.4, a contract that runs*

```python
# file: compile_clause()
if m == "duplicateValues":
    return (f"SELECT count({col}) - "
            f"count(DISTINCT {col}) FROM {t}")
if m == "invalidValues":
    return (f"SELECT count(*) FROM {t} "
            f"WHERE {col} NOT IN ({vals})")
```

**23 of 23** checks pass on today's 30,000-row table

- **Types first.** Each column's type is checked before its values.

#### [day3#breaking-vs-compatible] A rename fails the contract; an added column passes

*Lab 3.4, two proposed changes*

| Change | Contract result | Version |
| --- | --- | --- |
| A: `region_code` renamed to `region`; `amount_sar` sent as "SAR 120.00" | 3 checks fail: column missing, type changed, amount clause cannot run | 2.0.0 |
| B: a nullable `merchant_name` added | every check passes | 1.1.0 |
| A corrected description | nothing to check | 1.0.1 |

#### [day3#checkpoint-4] Which change breaks the contract?

*Checkpoint*

**Question:** The contract for `complaints_prepared` lists ten columns. Which change by the producer should fail the contract check?

- A. Adding a nullable column `merchant_name`
- B. Sending `amount_sar` as text such as "SAR 120.00"
- C. Correcting the description of `status`
- D. Publishing 31,000 rows instead of 30,000

#### [day3#lab-3-4] A contract that rejects a breaking change

Lab 3.4 · 25 min

Write an ODCS contract for the prepared complaints table, compile its clauses to SQL, pass it on today's table, and make a producer's breaking change fail while an added column passes.

[D3_4_write_contract_prepared.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D3_4_write_contract_prepared.ipynb)

- [ ] The schema part of the contract (7 min)
- [ ] Quality clauses from the rules (5 min)
- [ ] Compile the clauses to SQL and run them (7 min)
- [ ] A breaking change fails; an added column passes (6 min)
- [ ] ✱ Stretch: The version number each change needs

#### [day3#wrap-up] Three things to keep

*Day 3 · wrap-up*

- **A rule has an owner.** Dimension, attributes, threshold and a reason; judged on seeded defects and on clean data.
- **Precision before recall.** A wrong match blames someone; a tie returns NONE.
- **A contract that runs.** The consumer's columns and clauses, compiled to SQL, checked before publishing.

#### [day3#next] Day 4: Pipelines for analysis

*Next*

From a notebook to a pipeline that gives the same bytes twice, stops on a blocking rule, and explains why August's rate changed.

## Day 4: Pipelines for analysis

Package the preparation as a gated, traceable pipeline

#### [day4#title] Pipelines for analysis

*SDAIA Academy · Data Quality, Labelling and Pipelines for Analysis*

Day 4: Package the preparation as a gated, traceable pipeline

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-311

#### [day4#review-day3] What should the producer's change do to the contract?

*Review of Day 3*

**Question:** Abdulelah renames `region_code` to `region` in the prepared table, to match another system. The contract lists `region_code` as required. What should happen?

- A. The contract passes: the data is the same
- B. The contract passes with a warning; the version goes to 1.1.0
- C. Hatoon updates her report the morning it breaks
- D. The contract fails; the change waits for a 2.0.0 contract both agree

#### [day4#agenda] Pipelines for analysis

*Today*

- **Session 1 · From notebook to pipeline**: Hidden state out, steps with explicit inputs and outputs in, a run log, a lock file, and the same bytes twice
- **Session 2 · Gates in the pipeline**: Rules run inside the pipeline: warnings logged, bad rows quarantined, publication stopped by a blocking rule
- **Session 3 · Tracing a changed figure**: Lineage records and run logs show which change moved a published figure, one change at a time
- **Session 4 · Handing over prepared data**: The preparation section of a datasheet, with every number traceable to a run

### Session 1: From notebook to pipeline

#### [day4#s1] From notebook to pipeline

*Session 1*

- Find the hidden state that makes a notebook give different results
- Write preparation steps as functions with explicit inputs and outputs
- Show with a run log and a hash that two runs give the same table

#### [day4#notebook-twice] The same notebook on the same extract wrote two different tables

*Lab 4.1, the old notebook run twice*

| File | Monday | Tuesday |  |
| --- | --- | --- | --- |
| complaints_prepared.csv | `1fdbe892…` | `6796c999…` | different |
| monthly_rate.csv | `001a5f51…` | `56adaf2e…` | different |
| category_by_region.csv | `1cdc3da2…` | `1cdc3da2…` | same, today |

On Tuesday one cell was re-run after a comment was edited. Nothing else changed.

#### [day4#four-causes] Four ways a notebook stops being repeatable

*Hidden state*

- **The clock.** A `prepared_at` column from `now()`: every run is new bytes.
- **State changed in place.** Population multiplied by 1.01 inside a cell: run it twice, grow twice.
- **Unseeded randomness.** A shuffle before keeping the first copy: a different copy each run.
- **Unordered iteration.** Columns from a set of strings: the order follows Python's hash seed.

> **What goes wrong.** None of the four raises an error; the figure is simply different, and nobody can say which one is right.

#### [day4#steps-explicit] Each step names its inputs and outputs and returns its counts

*pipeline/steps.py*

1. **extract** four files → tables with a row id
2. **gate** rules → quarantine or stop
3. **clean** types, trimmed text
4. **dedupe** resubmissions within a day
5. **enrich** merchant, region, days to close
6. **publish** written last, renamed into place

Every step returns `rows_in`, `rows_out` and its parameters: the run log is made of these.

#### [day4#run-log] A run log answers "what made this table?" months later

*Lab 4.1, the runner*

```json
// file: run_log.json
{"run_id": "lab41", "extract_date": "2026-09-05",
 "code_version": "4f8d7d5",
 "lock_file_sha256": "…", "duckdb": "2.0.0",
 "inputs":  {"complaints_extract.csv.gz": "…"},
 "steps": [{"step": "dedupe", "rows_in": 30000,
            "rows_out": 30000, "params": {…}}],
 "rules": [...], "contract": {"checks": 23},
 "outputs": {"complaints_prepared.csv":
             "26132fbc707b22b3"}}
```

**same bytes** two runs a second apart wrote identical tables

- **Pinned versions.** `uv.lock` pins DuckDB 2.0.0; the run log records which one ran.

#### [day4#checkpoint-1] Which change makes the step repeatable?

*Checkpoint*

**Question:** A dedupe cell shuffles the complaints with `df.sample(frac=1)`, then keeps the first copy of each customer, merchant and product. Two runs keep different copies. What is the fix?

- A. Sort by received date and complaint id, then keep the first: a rule anyone can state
- B. Add `random_state=1` to the shuffle
- C. Run the cell only once per month
- D. Remove the dedupe step

#### [day4#lab-4-1] Steps, a runner and a lock file

Lab 4.1 · 25 min

Find four sources of nondeterminism in a preparation notebook, rewrite it as steps with a runner that writes a run log, and show two runs give the same bytes with the versions the lock file pins.

[D4_1_convert_preparation_notebook.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D4_1_convert_preparation_notebook.ipynb)

- [ ] Four sources of nondeterminism (5 min)
- [ ] Steps with explicit inputs and outputs (9 min)
- [ ] A runner that writes a run log (6 min)
- [ ] Two runs, the same bytes, the pinned versions (5 min)
- [ ] ✱ Stretch: A task runner for the steps

### Session 2: Gates in the pipeline

#### [day4#s2] Gates in the pipeline

*Session 2*

- Quarantine failing rows with the rule that caught them
- Stop the pipeline on a blocking rule before anything is published
- Show from a clean checkout that a run passes on clean data and fails on a seeded defect

#### [day4#gates-in-pipeline] Two gates stand between the extract and the published table

*Gates in the pipeline*

1. **extract**
2. **Gate 1 · rules** quarantine rows; stop on a block
3. **clean · dedupe · enrich**
4. **Gate 2 · contract** stop if the table breaks it
5. **publish**

> **Exit codes.** 0 published; 2 stopped, nothing written to `published/`, the run log says why.

#### [day4#quarantine-order] Judge every rule before deleting anything

*Lab 4.2, quarantine one rule at a time*

- **970** orphan actions when each rule deletes before the next runs
- **150** orphan actions when all rules judge the untouched tables

Deleting a quarantined complaint orphans its actions: a rule run after a delete judges a different table.

#### [day4#seeded-vs-corrected] Stopped on the halala batch; published once it was corrected

*Lab 4.2, the August batch*

| Extract | Exit | Published | Quarantined |
| --- | --- | --- | --- |
| Seeded, amounts in halalas | 2 | nothing; blocked by A01 and A02 | counted in the run log only |
| Corrected by the vendor (÷ 100) | 0 | 29,154 complaints | 915 complaints, 150 actions |
| Clean | 0 | 30,000 complaints | none |

#### [day4#clean-checkout] Run it from a clean checkout, not from your own folder

*Lab 4.2, evidence that it works*

- `git clone` into an empty folder, then run there.
- A forgotten file or a package only you have breaks the clone, not your folder.
- In the lab, the clone published the **same bytes** as the working folder, and stopped on the seeded extract.

```yaml
# file: pipeline/ci/pipeline.yml
- run: uv sync --locked
- run: uv run run.py --raw ../data/sources_clean ...
- run: |
    uv run run.py --raw ../data/sources ...
    test $? -eq 2
```

#### [day4#checkpoint-2] What does the report show after a blocked run?

*Checkpoint*

**Question:** The October run stops on A02: a channel's median amount tripled. Hatoon's monthly report reads `published/monthly_rate.csv`. What does it show the next morning?

- A. October's figures, with the bad channel removed
- B. Nothing: the file is deleted
- C. September's figures, unchanged, while the run log says why October stopped
- D. October's figures with a warning in the log

#### [day4#lab-4-2] Quarantine and block

Lab 4.2 · 25 min

Add the rules to the pipeline so it quarantines bad rows and stops on a blocking rule, then run it from a clean checkout on a clean extract and on the August batch.

[D4_2_make_pipeline_quarantine.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D4_2_make_pipeline_quarantine.ipynb)

- [ ] Quarantine rows with a reason (7 min)
- [ ] Stop on a blocking rule; publish only after every gate (7 min)
- [ ] From a clean checkout: pass on clean, fail on the defect (7 min)
- [ ] The CI workflow that runs it (4 min)
- [ ] ✱ Stretch: A warning that becomes a block after three runs

### Session 3: Tracing a changed figure

#### [day4#s3] Tracing a changed figure

*Session 3*

- Read run logs and lineage records to list what changed between two runs
- Attribute a changed figure to each change by recomputing one change at a time
- Write an incident note with root cause, affected outputs and correction

#### [day4#which-is-right] "Which figure for R04 in August is right: 48.06 or 39.14?"

*A stakeholder asks*

- **48.06** complaints per 100,000, published in September (run A)
- **39.14** the same month, republished in October (run B)

> **What goes wrong.** Answering "the newer one" because it has more data and newer code.

#### [day4#what-changed] Three things changed between the runs

*Lab 4.3, run logs and lineage*

| What | Run A, September | Run B, October |
| --- | --- | --- |
| Extract rows | 30,240 | 30,500 |
| Regions table | 2026.1 | 2026.2 (R04 population +5.5%) |
| Dedupe key | complaint id | customer, merchant, day |
| Code | a41c2e7 | c9d05b3 "dedupe on customer, merchant and day" |

#### [day4#one-at-a-time] The new dedupe key caused the fall

*Lab 4.3, one change at a time*

| Item | Value |
| --- | --- |
| September run | 48.06 |
| + late arrivals | 52.90 |
| + new population | 50.15 |
| + new dedupe key | 39.14 |

R04, August, per 100,000 residents. The new key dropped 72 complaints; only 4 were resubmissions.

#### [day4#corrected-answer] Neither: the corrected figure is 49.53

*Lab 4.3, the decision*

- Keep the late arrivals and the 2026.2 population.
- De-duplicate resubmissions only: same customer, merchant **and product** within one day.
- R04: 324 complaints, **49.53** per 100,000.
- All 13 regions' October figures were off by more than 1%; R04 by 21%.

- **The incident note.** What happened, root cause, other changes, affected outputs, correction, the answer to the stakeholder, prevention.

#### [day4#checkpoint-3] How do you find which change moved the figure?

*Checkpoint*

**Question:** Between two runs, the extract gained 260 rows, the population table changed and the dedupe key changed. R04's rate fell from 48.06 to 39.14. How do you attribute the fall?

- A. Blame the extract: it changed the most rows
- B. Divide the fall equally among the three changes
- C. Re-run October and see whether it repeats
- D. Start from September and apply the changes one at a time, recomputing each time

#### [day4#lab-4-3] Why the August rate changed

Lab 4.3 · 25 min

Use the run logs and lineage of two runs to find why August's complaint rate for one region changed, attribute the change, list the affected outputs and write the incident note.

[D4_3_use_run_logs.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D4_3_use_run_logs.ipynb)

- [ ] What changed between the two runs (6 min)
- [ ] Recompute one change at a time (9 min)
- [ ] Which outputs are affected (4 min)
- [ ] The incident note, and the answer to the stakeholder (6 min)
- [ ] ✱ Stretch: A lineage check that would have warned

### Session 4: Handing over prepared data

#### [day4#s4] Handing over prepared data

*Session 4*

- Write the preparation section of a datasheet for a prepared table
- Report agreement by language variety and the known limits
- Check every number in the section against the run that produced it

#### [day4#datasheet-why] A datasheet tells the next analyst what was done to the data

*Handing over prepared data*

- **Preprocessing.** Which extract and code; what was removed, by which rule; how duplicates were treated.
- **Labelling.** The guideline version; agreement overall and by language variety; the weakest category.
- **Known limits.** What the table cannot support, in plain words.

#### [day4#section-from-log] Every number comes from the run log

*Lab 4.4, the preprocessing part*

| Statement | Number | Taken from |
| --- | --- | --- |
| Complaints in the extract | 30,300 | extract rows_in |
| Set aside in quarantine | 915 | gate rows_in − rows_out |
| Resubmissions removed | 231 | dedupe rows_in − rows_out |
| Published | 29,154 | publish rows_out |
| Contract checks passed | 23 | contract.checks |

#### [day4#agreement-in-datasheet] Report agreement where it is weakest

*Lab 4.4, the labelling part*

| Item | Value |
| --- | --- |
| All, round 2 | 0.789 |
| MSA | 0.795 |
| Gulf dialect | 0.782 |
| English | 0.791 |
| Mixed | 0.743 |
| WARRANTY | 0.680 |

Krippendorff's alpha, pilot round 2 under guideline v1.1. Known limits follow from the lowest bars.

#### [day4#checkpoint-4] Where should the datasheet's numbers come from?

*Checkpoint*

**Question:** Hatoon's datasheet says "about 900 rows were removed by quality rules". The run log of the published table says 915 complaints and 150 actions were quarantined. What should the section say?

- A. "About 900 rows": close enough for readers
- B. "915 complaints and 150 case actions", taken from the run log, with the rules
- C. Nothing: the quarantine is an internal detail
- D. The counts from Lab 3.2's seeded run

#### [day4#lab-4-4] The datasheet's preparation section

Lab 4.4 · 25 min

Write the preparation section of the datasheet for the prepared complaints table from the run log, the rule results and the agreement report, and check every number against the run.

[D4_4_write_preparation_section.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D4_4_write_preparation_section.ipynb)

- [ ] What a user of the table needs to know (4 min)
- [ ] Fill the section from the run log and rule results (9 min)
- [ ] Agreement by variety, and the known limits (7 min)
- [ ] Every number traced to the run (5 min)
- [ ] ✱ Stretch: The contract and the datasheet name the same columns

#### [day4#wrap-up] Three things to keep

*Day 4 · wrap-up*

- **Same bytes twice.** No clock, no unseeded randomness, sorted outputs, pinned versions, a run log.
- **Gates before publishing.** Quarantine with a reason, block before anything is written, prove it from a clean checkout.
- **One change at a time.** Lineage says what changed; recomputing says how much; the note says which figure is right.

#### [day4#next] Capstone: Al-Ghadaf Municipality

*Next*

A guideline, agreement, rules, a contract and a gated pipeline for maintenance requests, presented with the seeded defect your pipeline must stop.

## Capstone: Capstone project presentations

A labelled, quality-gated table for Al-Ghadaf Municipality, reviewed live with a seeded defect

#### [capstone#title] Capstone project presentations

*SDAIA Academy · Data Quality, Labelling and Pipelines for Analysis*

Capstone: A labelled, quality-gated table for Al-Ghadaf Municipality, reviewed live with a seeded defect

Data Science Track · 4 teaching days + capstone day · 10 min talk and demo · DS-311

#### [capstone#agenda] How the presentations run

*Capstone*

- **Expectations and final prep**: the case, the rubric, a last rehearsal
- **Presentations with a seeded defect**: ten minutes each, the defect run live
- **Review and closing**: peer feedback, the trainer's review, what next

#### [capstone#the-case] Al-Ghadaf Municipality wants a figure it can defend

*The capstone case*

- **The requests.** 2,000 maintenance requests in Arabic, Gulf dialect, English and a mix; five categories with three boundaries to decide.
- **The tables.** The request extract, seven districts with populations, contractors and work orders with costs.
- **The figure.** Requests per 10,000 residents by district and category, and repair cost per contractor.

The same chain as Bayyin's: guideline and agreement, rules and a contract, a gated pipeline, an incident note.

#### [capstone#hand-in] What each repository holds

*The repository*

- A **guideline** with a change log tied to measured disagreements, and agreement for two pilot rounds.
- **Rules** with owners, dimensions, thresholds and severities, and an **ODCS contract**.
- A **pipeline** with a lock file and a CI workflow, run from a clean checkout.
- **Two run logs**: one passing on clean data, one stopped by a defect the team seeded, with its **incident note**.
- A **README** reporting agreement and rule results from the two runs, and a datasheet section.

#### [capstone#rubric] The rubric

*How presentations are scored*

| Item | Value |
| --- | --- |
| Guideline and agreement | 25% |
| Rules and contract | 25% |
| Pipeline | 25% |
| Incident handling | 15% |
| Reproducibility | 10% |

> **Show results from at least two measured runs.** A claim without a number is a plan, not a result.

#### [capstone#format] 10 minutes for each team, most of it live

*Format*

- **1 · Your table · 2'.** The figure, your agreement by variety, your rules. One slide or the README.
- **2 · The seeded defect · 6'.** Clone, run on the assessor's extract, show it stop or quarantine, trace it to its rule and rows.
- **3 · Questions · 2'.** Two questions on the guideline and the agreement figures.

> **Peer feedback.** After each talk, everyone writes one strength, one question and one suggestion.

#### [capstone#seeded-review] What the assessor looks for in six minutes

*The live review*

1. **1 · Clean clone** no local files
2. **2 · Run** on the seeded extract
3. **3 · Stop or set aside** by which rule, how many rows
4. **4 · Trace** rows, cause, affected outputs

> **The question to answer.** "Which figure would have been wrong, and by how much?"

#### [capstone#running-order] Who presents when

*Running order*

| # | Team | Seed and defect |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 8 |  |  |

#### [capstone#final-prep] Final prep · 20 minutes

*Before the first presentation*

Clone your repository on this laptop, run it once on clean data, and check your README's numbers.

#### [capstone#now-presenting] Table, defect and questions

*Now presenting*

#### [capstone#review] What the presentations showed

*Trainer review*

- **Strongest patterns.** What several projects got right.
- **Common gaps.** What most projects would fix next.
- **One surprise.** Something nobody expected.

#### [capstone#what-next] Keep going

*After the course*

- **The follow-up task:** apply one rule set and a contract to a table from your own work within four weeks, and send the run logs (labs/follow_up.md).
- **Your project stays yours:** keep it reproducible and add the next improvement you named today.
- **DS-306:** measuring the labels a model makes against a gold set, the step after this week's.
- **AE-306:** contracts, orchestration and quality tests at platform scale.

#### [capstone#thanks] Thank you

*SDAIA Academy*

Data Quality, Labelling and Pipelines for Analysis
