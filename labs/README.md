# Data Quality, Labelling and Pipelines for Analysis: labs

## Quick start

- Google Colab: open a notebook from the course page; its first cell clones this repository.
- Locally: clone the repository, then open the notebooks in `labs/` with Jupyter.

| Unit | Session | Notebook |
|---|---|---|
| Day 1 | Session 1 · What a label measures | [`D1_1_label_40_complaints.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D1_1_label_40_complaints.ipynb) |
| Day 1 | Session 2 · Writing a guideline | [`D1_2_write_definitions_rules.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D1_2_write_definitions_rules.ipynb) |
| Day 1 | Session 3 · Agreement statistics | [`D1_3_compute_kappa_alpha.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D1_3_compute_kappa_alpha.ipynb) |
| Day 1 | Session 4 · Adjudication and revision | [`D1_4_adjudicate_30_disagreements.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D1_4_adjudicate_30_disagreements.ipynb) |
| Day 2 | Session 1 · Sampling a golden set | [`D2_1_draw_stratified_golden.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D2_1_draw_stratified_golden.ipynb) |
| Day 2 | Session 2 · Gold questions and review queues | [`D2_2_set_gold_question.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D2_2_set_gold_question.ipynb) |
| Day 2 | Session 3 · Rater drift and workload | [`D2_3_find_drifting_rater.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D2_3_find_drifting_rater.ipynb) |
| Day 2 | Session 4 · Cost and model pre-labels | [`D2_4_compare_cost_per.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D2_4_compare_cost_per.ipynb) |
| Day 3 | Session 1 · Profiling to rules | [`D3_1_profile_four_source.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D3_1_profile_four_source.ipynb) |
| Day 3 | Session 2 · Rules with severity | [`D3_2_implement_warning_blocking.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D3_2_implement_warning_blocking.ipynb) |
| Day 3 | Session 3 · Duplicates and merchant matching | [`D3_3_match_merchant_names.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D3_3_match_merchant_names.ipynb) |
| Day 3 | Session 4 · A data contract | [`D3_4_write_contract_prepared.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D3_4_write_contract_prepared.ipynb) |
| Day 4 | Session 1 · From notebook to pipeline | [`D4_1_convert_preparation_notebook.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D4_1_convert_preparation_notebook.ipynb) |
| Day 4 | Session 2 · Gates in the pipeline | [`D4_2_make_pipeline_quarantine.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D4_2_make_pipeline_quarantine.ipynb) |
| Day 4 | Session 3 · Tracing a changed figure | [`D4_3_use_run_logs.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D4_3_use_run_logs.ipynb) |
| Day 4 | Session 4 · Handing over prepared data | [`D4_4_write_preparation_section.ipynb`](https://colab.research.google.com/github/SDAIAAcademy/ds-311/blob/main/labs/D4_4_write_preparation_section.ipynb) |

The notebooks are generated from the percent-format sources in `labs/_src/` by `labs/_tools/py2nb.py` (`uv run python _tools/py2nb.py` from `labs/`), which also writes the solutions to `labs/solutions/`. Edit the sources, not the notebooks.

## Setup

- **Colab:** nothing to install; the first cell of each notebook clones the repository and installs `requirements-colab.txt`.
- **Locally:** install [uv](https://docs.astral.sh/uv/), then from `labs/`: `uv sync`, `uv run python prepare_data.py` (only if you change the generator; the data is committed), and `uv run jupyter lab`. Run `00_setup_check.ipynb` first.
- **Model key (Lab 2.4 only):** copy `.env.example` to `.env` and set a free OpenRouter key. Without one, `bayyin.chat()` uses a scripted stand-in and prints that it did. No model is downloaded; everything runs on a laptop CPU or Colab.
- **Quick mode:** `DS311_QUICK=1` shrinks bootstrap repetitions for a fast run through every notebook.

## The case and its data

Bayyin Consumer Protection Office (مكتب بيّن لحماية المستهلك) is a fictional regulator. `prepare_data.py` (standard library, seed 311) writes every file in `data/`; the same seed writes the same bytes.

| Folder | What it holds | Used in |
|---|---|---|
| `data/corpus/` | 30,000 synthetic complaints (text, language variety) and their index | Days 1 and 2 |
| `data/pilot/` | 300 complaints labelled by R1 to R3 in two rounds; the 40 to label; edge cases; 30 disagreements | Day 1 |
| `data/ops/` | a ten-day operations round (six raters, 2,000 items), the gold bank, the design trial, 40 complaints to pre-label | Day 2 |
| `data/sources/`, `data/sources_clean/` | the portal extract, merchant registry, regions and case actions, with and without nine seeded defects | Days 3 and 4 |
| `data/matching/` | 600 raw merchant names, 300 of them labelled | Lab 3.3 |
| `data/runs/` | two refreshes (September and October) with run logs, lineage and figures | Lab 4.3 |
| `data/reference/` | reference results that the safety-net cells load when an exercise is not finished, and the trainer's lists | all labs |

Every lab starts from these files, never from another lab's output: a participant who did not finish Lab 3.2 starts Lab 3.3 normally. Lab outputs go to `labs/artifacts/` (ignored by git).

## Helpers and the pipeline

- `bayyin.py`: reading data (`B.read`), checks (`B.check`), agreement (`cohen_kappa`, `krippendorff_alpha`, `bootstrap`, `wilson`), masking patterns, and `chat()` with its stand-in.
- `pipeline/`: Bayyin's preparation pipeline (`steps.py`, `rules.py`, `contract.py`, `run.py`, `contract.odcs.yaml`, its own `uv.lock`, and `ci/pipeline.yml`). Run it from `labs/pipeline/` with `uv run run.py --raw ../data/sources_clean --regions ../data/sources_clean/regions.csv --out out`.
- `capstone/`: the Al-Ghadaf Municipality generator and brief.
- `follow_up.md`: the pre-work and the tracked follow-up task. `solutions/answer_key.md`: the numbers each solution prints.

## AI policy in the labs

AI-off in Labs 1.1 and 3.1. AI-tutor in the others: an assistant may explain an error, never write the guideline, the rules or the numbers. Only Lab 2.4 sends text to a model, and only after masking; anything with a residual identifier is classified Restricted and is not sent.
