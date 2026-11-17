---
course: "Data Quality, Labelling and Pipelines for Analysis"
code: "DS-311"
version: "2027.1.0"
deck: "day2"
day: 2
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-311/slides/day2.html"
---

# Data Quality, Labelling and Pipelines for Analysis

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
