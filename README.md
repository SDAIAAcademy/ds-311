<!-- academy:title -->
# Data Quality, Labelling and Pipelines for Analysis

جودة البيانات والوسم ومسارات إعدادها للتحليل

Data Science Track · SDAIA Academy · DS-311 · Level 300

Build the labels, rules, contract and gated pipeline an analysis depends on, and trace a figure that changed

Participants build the data an analysis depends on for Bayyin Consumer Protection Office, a fictional regulator holding 30,000 synthetic complaint records in Arabic and English. They write a labelling guideline, pilot it, measure agreement and adjudicate, run golden-question checks and review queues across a rater team, turn analysts' requirements into quality rules and a data contract, and package the preparation as a reproducible pipeline that stops on those rules. Measuring model-made labels is DS-306; platform-scale data engineering is AE-306.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

**Course page:** https://sdaiaacademy.github.io/ds-311/
<!-- /academy:title -->

## Outcomes

| | Outcomes | Level | Evidence |
|---|---|---|---|
| LO1 | Draft a labelling guideline with definitions, decision rules and edge cases, and revise it after a pilot, given 300 synthetic complaints labelled by three raters | Applied | a versioned guideline whose change log ties each revision to a measured disagreement |
| LO2 | Compute chance-corrected agreement by category and rater, and adjudicate the disagreements, given two rounds of pilot labels | Applied | an agreement report with intervals and an adjudicated set |
| LO3 | Configure a labelling workflow with golden-question checks, review queues and rater-drift monitoring, given a simulated round of 2,000 items from six raters, one of whom drifts | Applied | a quality-control report that flags the drifting rater and states cost per accepted label |
| LO4 | Implement quality rules with thresholds and severities, and a data contract for the prepared table, given four source tables with seeded defects | Applied | rules and a contract that catch each defect and reject a breaking schema change |
| LO5 | Build a reproducible preparation pipeline from raw extracts to an analysis-ready table that stops on a blocking rule, given a repository with continuous integration | Performance | run logs that pass on clean data and fail on a seeded defect from a clean checkout |
| LO6 | Diagnose why an analytical figure changed after a data refresh and decide on the correction, given two runs, their lineage records and a stakeholder asking which figure is right | Performance | an incident note with root cause, affected outputs and correction |

<!-- academy:units -->
## Units

| Unit | Title | Sessions | Slides |
|---|---|---|---|
| Day 1 | Labels are measurements | What a label measures; Writing a guideline; Agreement statistics; Adjudication and revision | [`slides/day1.html`](slides/day1.html) |
| Day 2 | Golden sets and labelling operations | Sampling a golden set; Gold questions and review queues; Rater drift and workload; Cost and model pre-labels | [`slides/day2.html`](slides/day2.html) |
| Day 3 | Rules and contracts | Profiling to rules; Rules with severity; Duplicates and merchant matching; A data contract | [`slides/day3.html`](slides/day3.html) |
| Day 4 | Pipelines for analysis | From notebook to pipeline; Gates in the pipeline; Tracing a changed figure; Handing over prepared data | [`slides/day4.html`](slides/day4.html) |
| Capstone | Capstone project presentations |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## Case study

**REPLACE: the name of the fictional organisation every lab works on.** REPLACE: two sentences on the case study and its synthetic data

<!-- academy:labs -->
## Labs

Every lab is a notebook in `labs/`. Open it in Google Colab from the course page, or run it locally with `uv`. Exercises raise `NotImplementedError` until they are done; the reference versions are in `labs/solutions/`.

| | Session | Lab | File |
|---|---|---|---|
| 1.1 | Day 1 · Session 1 | Label 40 complaints, then compare | [`D1_1_label_40_complaints.ipynb`](labs/D1_1_label_40_complaints.ipynb) |
| 1.2 | Day 1 · Session 2 | Guideline v1.0 for six categories | [`D1_2_write_definitions_rules.ipynb`](labs/D1_2_write_definitions_rules.ipynb) |
| 1.3 | Day 1 · Session 3 | Kappa and alpha on the pilot | [`D1_3_compute_kappa_alpha.ipynb`](labs/D1_3_compute_kappa_alpha.ipynb) |
| 1.4 | Day 1 · Session 4 | Adjudicate 30, revise, measure again | [`D1_4_adjudicate_30_disagreements.ipynb`](labs/D1_4_adjudicate_30_disagreements.ipynb) |
| 2.1 | Day 2 · Session 1 | A stratified golden set | [`D2_1_draw_stratified_golden.ipynb`](labs/D2_1_draw_stratified_golden.ipynb) |
| 2.2 | Day 2 · Session 2 | Gold checks and routing | [`D2_2_set_gold_question.ipynb`](labs/D2_2_set_gold_question.ipynb) |
| 2.3 | Day 2 · Session 3 | Find the drifting rater | [`D2_3_find_drifting_rater.ipynb`](labs/D2_3_find_drifting_rater.ipynb) |
| 2.4 | Day 2 · Session 4 | Cost per accepted label | [`D2_4_compare_cost_per.ipynb`](labs/D2_4_compare_cost_per.ipynb) |
| 3.1 | Day 3 · Session 1 | Profile four tables, propose rules | [`D3_1_profile_four_source.ipynb`](labs/D3_1_profile_four_source.ipynb) |
| 3.2 | Day 3 · Session 2 | Warning and blocking rules | [`D3_2_implement_warning_blocking.ipynb`](labs/D3_2_implement_warning_blocking.ipynb) |
| 3.3 | Day 3 · Session 3 | Merchant names across two scripts | [`D3_3_match_merchant_names.ipynb`](labs/D3_3_match_merchant_names.ipynb) |
| 3.4 | Day 3 · Session 4 | A contract that rejects a breaking change | [`D3_4_write_contract_prepared.ipynb`](labs/D3_4_write_contract_prepared.ipynb) |
| 4.1 | Day 4 · Session 1 | Steps, a runner and a lock file | [`D4_1_convert_preparation_notebook.ipynb`](labs/D4_1_convert_preparation_notebook.ipynb) |
| 4.2 | Day 4 · Session 2 | Quarantine and block | [`D4_2_make_pipeline_quarantine.ipynb`](labs/D4_2_make_pipeline_quarantine.ipynb) |
| 4.3 | Day 4 · Session 3 | Why the August rate changed | [`D4_3_use_run_logs.ipynb`](labs/D4_3_use_run_logs.ipynb) |
| 4.4 | Day 4 · Session 4 | The datasheet's preparation section | [`D4_4_write_preparation_section.ipynb`](labs/D4_4_write_preparation_section.ipynb) |
<!-- /academy:labs -->

## Capstone

A labelled, quality-gated analysis table for a second synthetic case (municipal maintenance requests), in a public repository whose README reports agreement and rule results from two runs, defended in a ten-minute review in which the assessor seeds a defect

**Submission:** REPLACE: what participants submit and how: a public repository link, or a shared folder for a course without code

## Prerequisites

- DS-202 Data Acquisition, Preparation and Quality
- FN-102 Command Line, Git and Reproducible Projects
- Writes Python functions and SQL queries
- Uses Git and a lock-file environment

<!-- academy:tools -->
## Tools

Each line is a capability; the examples are interchangeable.

- **Annotation tool:** Label Studio, Argilla, a spreadsheet with locked validation rules
- **Validation framework:** Pandera, Great Expectations, Soda Core
- **Data contract specification:** Open Data Contract Standard, contract checks compiled to SQL tests
- **Data processing and pipeline runner:** DuckDB or Polars with a task runner, Dagster with OpenLineage events
- **Language model for pre-labels, through a chat-completions style endpoint:** a locally served open-weight model, a free hosted open-weight model
<!-- /academy:tools -->

<!-- academy:sources -->
## Sources

### Labelling and agreement

- [Klaus Krippendorff: Computing Krippendorff's Alpha-Reliability](https://repository.upenn.edu/handle/20.500.14332/2089)
- [Artstein and Poesio: Inter-Coder Agreement for Computational Linguistics (2008)](https://aclanthology.org/J08-4004/)
- [Label Studio documentation](https://labelstud.io/guide/)
- [Argilla documentation](https://docs.argilla.io/)

### Rules, contracts and pipelines

- [Open Data Contract Standard (ODCS)](https://bitol-io.github.io/open-data-contract-standard/latest/)
- [ODCS v3.2.0 release](https://github.com/bitol-io/open-data-contract-standard/releases/tag/v3.2.0)
- [Pandera documentation](https://pandera.readthedocs.io/en/stable/)
- [Great Expectations documentation](https://docs.greatexpectations.io/docs/home/)
- [Soda documentation](https://docs.soda.io/)
- [DuckDB documentation](https://duckdb.org/docs/stable/)
- [uv: project layout and the lock file](https://docs.astral.sh/uv/concepts/projects/layout/)
- [OpenLineage object model](https://openlineage.io/docs/spec/object-model/)
- [Dagster documentation](https://docs.dagster.io/)
- [Gebru et al.: Datasheets for Datasets](https://arxiv.org/abs/1803.09010)

### National references

- [NDMO: Data Management and Personal Data Protection Standards](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataManagementPersonalDataProtectionStandards.pdf)
- [NDMO: Data Classification Policy](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
- [Personal Data Protection Law](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [Implementing Regulation of the Personal Data Protection Law](https://sdaia.gov.sa/en/SDAIA/about/Documents/ImplementingRegulationPersonalDataProtectionLaw.pdf)
- [SDAIA: Generative AI Guidelines for Government](https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf)
<!-- /academy:sources -->

### National references

- NDMO Data Management and Personal Data Protection Standards (Data Quality, and Data Catalog and Metadata domains): REPLACE: the address of the official text
- NDMO Data Classification Policy: REPLACE: the address of the official text
- Personal Data Protection Law and its implementing regulations: REPLACE: the address of the official text
- SDAIA Generative AI Guidelines for Government: REPLACE: the address of the official text
