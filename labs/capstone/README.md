# Capstone · Al-Ghadaf Municipality (بلدية الغضف)

Al-Ghadaf Municipality, a fictional municipality of seven districts, receives about 2,000
maintenance requests a year through its app, its call centre and its website, in Arabic, Gulf
dialect, English and a mix. Its planning team wants a monthly figure: **requests per 10,000
residents by district and category**, and the average repair cost per contractor. Nobody has
labelled the requests consistently, and the extracts have never been checked.

You build what Bayyin built this week, for Al-Ghadaf: a labelling guideline tested by agreement, the
quality rules and a contract, and a pipeline that publishes the figure only when the data passes.

## The data

```
cd labs/capstone
python make_case.py --out data              # your team's case, seed 2027
python make_case.py --out data --seed 41    # a variant, if the trainer gives your team another seed
```

| File | What it holds |
|---|---|
| `data/requests_text.csv` | 2,000 requests to label: id, text, language variety |
| `data/pilot_round1.csv`, `pilot_round2.csv` | 150 requests labelled by three raters, before and after a guideline revision |
| `data/sources/requests_extract.csv.gz` | the request extract of 2027-03-05, with the reference category |
| `data/sources/districts.csv` | seven districts and their populations (version 2027.1) |
| `data/sources/contractors.csv`, `work_orders.csv.gz` | contractors and the work orders with their cost in riyals |

The five categories are `ROAD`, `LIGHT`, `WATER`, `WASTE` and `PARK`. Some requests sit on a boundary
(a water leak that opened a hole in the road; lights inside a park; rubbish inside a park): your
guideline must decide them.

## What to hand in

A public GitHub repository with:

1. **The guideline** (`guideline.md`): definitions, decision rules for the boundaries, edge cases, a
   version and a change log that ties each revision to a measured disagreement.
2. **Agreement** for the two pilot rounds: kappa by rater pair, Krippendorff's alpha overall, by
   category and by language variety, with bootstrap intervals.
3. **Rules** for the four source tables, each with an owner, a dimension, a threshold and a severity,
   and an **ODCS v3.2.0 contract** for the prepared table.
4. **The pipeline**: steps, a runner that writes a run log and lineage, a lock file, and a CI
   workflow that runs it from a clean checkout.
5. **Two run logs**: one that passes on the clean extract, one stopped by a defect you seeded
   yourself (`--defect`), and an **incident note** for it.
6. **A README** that reports agreement and rule results from the two runs, and a datasheet
   preparation section whose numbers come from the run log.

## The live review (10 minutes)

The assessor runs `make_case.py` with a defect you have not seen (one of `duplicates`,
`district_codes`, `cost_units`, `closed_before`, `future_dates`) and gives you the extract. From a
clean checkout of your repository you run the pipeline on it, show that it stops or quarantines, and
trace the defect to its rule and its rows. Then two questions on your guideline and your agreement
figures.

## Rubric

| Criterion | Weight | Full marks look like |
|---|---|---|
| Guideline and agreement | 25 | Boundaries decided by rules, change log tied to measured disagreements, alpha by variety with intervals |
| Rules and contract | 25 | Every rule has an owner, dimension, threshold and severity; the contract rejects a breaking change |
| Pipeline | 25 | Same bytes twice; quarantine with reasons; stops before publishing on a blocking rule |
| Incident handling | 15 | The seeded defect caught and traced live; an incident note with root cause, affected outputs and correction |
| Reproducibility | 10 | Runs from a clean checkout with the lock file; CI green on clean data |

AI policy: AI-full in the capstone, defended live. Any model pre-label is checked by a person,
never accepted unseen, and no request text classified Restricted or above is sent to a hosted model.

## README template for your repository

```markdown
# Al-Ghadaf maintenance requests: a labelled, quality-gated table

## The figure
Requests per 10,000 residents by district and category, monthly; average repair cost per contractor.

## Guideline
Version, link, and the change log in one table: version, change, the disagreement that caused it.

## Agreement
| | Round 1 | Round 2 |
|---|---|---|
| Alpha, all (95% interval) | | |
| By variety: msa, gulf, english, mixed | | |
| Weakest category | | |

## Rules and contract
One row per rule: id, dimension, owner, threshold, severity. Link to the contract.

## Two runs
| Run | Extract | Exit | Quarantined by rule | Blocked by | Published rows |
|---|---|---|---|---|---|
| clean | | 0 | | | |
| seeded (defect: ...) | | 2 | | | |

## Incident note
Root cause, affected outputs, correction.

## Datasheet: preparation
Generated from the run log; every number traced.

## Reproduce
git clone ... && cd pipeline && uv sync --locked && uv run run.py ...
```
