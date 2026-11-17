---
course: "Data Quality, Labelling and Pipelines for Analysis"
code: "DS-311"
version: "2027.1.0"
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-311/index.html"
---

# Data Quality, Labelling and Pipelines for Analysis

جودة البيانات والتوسيم وخطوط إعدادها للتحليل

Data Science Track · 4 teaching days + capstone day · 26 hours · Level 300

Build the labels, rules, contract and gated pipeline an analysis depends on, and trace a figure that changed

Participants build the data an analysis depends on for Bayyin Consumer Protection Office, a fictional regulator holding 30,000 synthetic complaint records in Arabic and English. They write a labelling guideline, pilot it, measure agreement and adjudicate, run golden-question checks and review queues across a rater team, turn analysts' requirements into quality rules and a data contract, and package the preparation as a reproducible pipeline that stops on those rules. Measuring model-made labels is DS-306; platform-scale data engineering is AE-306.

**Who it is for:** Practitioners. Data scientists and analysts who have completed the level 200 set or can show equivalent work: an analysis they framed, carried out and explained to a stakeholder.

**Format:** Intensive: 4 teaching days of four sessions and a capstone day, with guided pre-work and a tracked follow-up task

## The case study

**Bayyin Consumer Protection Office.** Bayyin is a fictional consumer protection regulator with 30,000 synthetic complaints in Modern Standard Arabic, Gulf dialect, English and code-switched text, four source tables and a monthly complaint rate per 100,000 residents that its analysts publish. Participants write and pilot a six-category labelling guideline, measure and adjudicate agreement, run gold checks, review queues and drift monitoring over six raters, turn requirements into severity rules and an open-standard contract, and package the preparation as a pipeline that quarantines, blocks and leaves lineage. All data is synthetic and generated with a fixed seed.

## The course

### Day 1: Labels are measurements

Slides: https://sdaiaacademy.github.io/ds-311/slides/day1.md

- **Session 1: What a label measures**
  - Explain a label as a measurement with a construct, a scale and an error
  - Label complaints without a guideline and measure raw agreement with two neighbours
  - Name the category pairs where people disagree and why
  - [Lab 1.1: Label 40 complaints, then compare (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D1_1_label_40_complaints.ipynb)
- **Session 2: Writing a guideline**
  - Write a definition with includes and excludes for each category
  - Order decision rules so that every overlap resolves to one label
  - Record edge cases, dialect notes and the limits on distressing content
  - [Lab 1.2: Guideline v1.0 for six categories (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D1_2_write_definitions_rules.ipynb)
- **Session 3: Agreement statistics**
  - Compute kappa for each pair of raters and explain the chance correction
  - Compute Krippendorff's alpha from a coincidence matrix
  - Report agreement by category and language with bootstrap intervals
  - [Lab 1.3: Kappa and alpha on the pilot (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D1_3_compute_kappa_alpha.ipynb)
- **Session 4: Adjudication and revision**
  - Adjudicate disagreements with a decision and a reason code
  - Tie every guideline revision to a measured disagreement in a change log
  - Measure whether the revision raised agreement in the next round
  - [Lab 1.4: Adjudicate 30, revise, measure again (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D1_4_adjudicate_30_disagreements.ipynb)

### Day 2: Golden sets and labelling operations

Slides: https://sdaiaacademy.github.io/ds-311/slides/day2.md

- **Session 1: Sampling a golden set**
  - Explain why a simple random sample misses rare categories and dialects
  - Stratify on fields known before labelling, with a floor per stratum
  - Weight a stratified sample back to the population
  - [Lab 2.1: A stratified golden set (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D2_1_draw_stratified_golden.ipynb)
- **Session 2: Gold questions and review queues**
  - Estimate each rater's gold accuracy with an interval
  - Set a pass rule that needs a minimum number of gold answers
  - Route items to acceptance, adjudication or a restricted queue
  - [Lab 2.2: Gold checks and routing (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D2_2_set_gold_question.ipynb)
- **Session 3: Rater drift and workload**
  - Track gold accuracy per rater over time
  - Flag drift against a rater's own baseline, not the team average
  - Check workload and distressing-content time against the guideline
  - [Lab 2.3: Find the drifting rater (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D2_3_find_drifting_rater.ipynb)
- **Session 4: Cost and model pre-labels**
  - Compute cost per accepted label for a labelling design
  - Mask personal data and classify what may leave the organisation before a model call
  - Compare double, audited single and model-assisted labelling on cost and error
  - [Lab 2.4: Cost per accepted label (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D2_4_compare_cost_per.ipynb)

### Day 3: Rules and contracts

Slides: https://sdaiaacademy.github.io/ds-311/slides/day3.md

- **Session 1: Profiling to rules**
  - Profile tables for completeness, uniqueness, validity, consistency, accuracy and timeliness
  - Read anomalies from a profile without help
  - Write a rule with an owner, a dimension, a threshold and a business reason
  - [Lab 3.1: Profile four tables, propose rules (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D3_1_profile_four_source.ipynb)
- **Session 2: Rules with severity**
  - Write a rule as a query that returns the failing rows
  - Give each rule a severity: warn, quarantine or block
  - Show that the rules catch each seeded defect and stay quiet on clean data
  - [Lab 3.2: Warning and blocking rules (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D3_2_implement_warning_blocking.ipynb)
- **Session 3: Duplicates and merchant matching**
  - Tell exact duplicates from resubmissions
  - Normalise Arabic and Latin names and compare them through a transliteration key
  - Choose a match threshold from precision and recall on labelled pairs
  - [Lab 3.3: Merchant names across two scripts (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D3_3_match_merchant_names.ipynb)
- **Session 4: A data contract**
  - Write a contract for a table in the Open Data Contract Standard
  - Compile its quality clauses to SQL checks
  - Tell a breaking schema change from a compatible one
  - [Lab 3.4: A contract that rejects a breaking change (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D3_4_write_contract_prepared.ipynb)

### Day 4: Pipelines for analysis

Slides: https://sdaiaacademy.github.io/ds-311/slides/day4.md

- **Session 1: From notebook to pipeline**
  - Find the hidden state that makes a notebook give different results
  - Write preparation steps as functions with explicit inputs and outputs
  - Show with a run log and a hash that two runs give the same table
  - [Lab 4.1: Steps, a runner and a lock file (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D4_1_convert_preparation_notebook.ipynb)
- **Session 2: Gates in the pipeline**
  - Quarantine failing rows with the rule that caught them
  - Stop the pipeline on a blocking rule before anything is published
  - Show from a clean checkout that a run passes on clean data and fails on a seeded defect
  - [Lab 4.2: Quarantine and block (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D4_2_make_pipeline_quarantine.ipynb)
- **Session 3: Tracing a changed figure**
  - Read run logs and lineage records to list what changed between two runs
  - Attribute a changed figure to each change by recomputing one change at a time
  - Write an incident note with root cause, affected outputs and correction
  - [Lab 4.3: Why the August rate changed (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D4_3_use_run_logs.ipynb)
- **Session 4: Handing over prepared data**
  - Write the preparation section of a datasheet for a prepared table
  - Report agreement by language variety and the known limits
  - Check every number in the section against the run that produced it
  - [Lab 4.4: The datasheet's preparation section (25 min)](https://sdaiaacademy.github.io/ds-311/labs/D4_4_write_preparation_section.ipynb)

### Capstone: Capstone project presentations

Slides: https://sdaiaacademy.github.io/ds-311/slides/capstone.md

## Capstone

A labelled, quality-gated analysis table for a second synthetic case (municipal maintenance requests), in a public repository whose README reports agreement and rule results from two runs, defended in a ten-minute review in which the assessor seeds a defect

**What you submit:** A public GitHub repository link: the labelling guideline with its change log, agreement from two pilot rounds, the rules and the ODCS contract, the pipeline with its lock file and CI workflow, run logs of two runs (one passing on clean data, one stopped by a seeded defect) and an incident note, with a README that reports agreement and rule results from the two runs. Then a ten-minute live review: the assessor seeds a defect in the data and the participant runs the pipeline from a clean checkout, catches it and traces it.

**Rubric:**

- Guideline and agreement: 25%
- Rules and contract: 25%
- Pipeline: 25%
- Incident handling: 15%
- Reproducibility: 10%

## Outcomes

- **LO1** Draft a labelling guideline with definitions, decision rules and edge cases, and revise it after a pilot, given 300 synthetic complaints labelled by three raters (Applied) Evidence: a versioned guideline whose change log ties each revision to a measured disagreement
- **LO2** Compute chance-corrected agreement by category and rater, and adjudicate the disagreements, given two rounds of pilot labels (Applied) Evidence: an agreement report with intervals and an adjudicated set
- **LO3** Configure a labelling workflow with golden-question checks, review queues and rater-drift monitoring, given a simulated round of 2,000 items from six raters, one of whom drifts (Applied) Evidence: a quality-control report that flags the drifting rater and states cost per accepted label
- **LO4** Implement quality rules with thresholds and severities, and a data contract for the prepared table, given four source tables with seeded defects (Applied) Evidence: rules and a contract that catch each defect and reject a breaking schema change
- **LO5** Build a reproducible preparation pipeline from raw extracts to an analysis-ready table that stops on a blocking rule, given a repository with continuous integration (Performance) Evidence: run logs that pass on clean data and fail on a seeded defect from a clean checkout
- **LO6** Diagnose why an analytical figure changed after a data refresh and decide on the correction, given two runs, their lineage records and a stakeholder asking which figure is right (Performance) Evidence: an incident note with root cause, affected outputs and correction

## Tools

- **Annotation tool:** Label Studio, Argilla, a spreadsheet with locked validation rules
- **Validation framework:** Pandera, Great Expectations, Soda Core
- **Data contract specification:** Open Data Contract Standard, contract checks compiled to SQL tests
- **Data processing and pipeline runner:** DuckDB or Polars with a task runner, Dagster with OpenLineage events
- **Language model for pre-labels, through a chat-completions style endpoint:** a locally served open-weight model, a free hosted open-weight model

## Prerequisites

- DS-202 Data Acquisition, Preparation and Quality
- FN-102 Command Line, Git and Reproducible Projects
- Writes Python functions and SQL queries
- Uses Git and a lock-file environment
- Setup: a laptop CPU with uv, or Google Colab. Nothing downloads a model; one lab calls a free hosted model and runs without a key on a stand-in. Run 00_setup_check before Day 1; see labs/README.md.

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

---

SDAIA Academy · Data Science Track · Data Quality, Labelling and Pipelines for Analysis

Course version 2027.1.0 · engine 1.0.0 · built 2026-11-15 · commit 7240e93
