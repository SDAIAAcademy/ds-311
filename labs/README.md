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
