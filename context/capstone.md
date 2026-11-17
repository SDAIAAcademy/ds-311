---
course: "Data Quality, Labelling and Pipelines for Analysis"
code: "DS-311"
version: "2027.1.0"
deck: "capstone"
day: 5
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-311/slides/capstone.html"
---

# Data Quality, Labelling and Pipelines for Analysis

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
