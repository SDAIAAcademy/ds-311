---
course: "Data Quality, Labelling and Pipelines for Analysis"
code: "DS-311"
version: "2027.1.0"
deck: "day4"
day: 4
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-311/slides/day4.html"
---

# Data Quality, Labelling and Pipelines for Analysis

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
