"""Write the reference results the labs' safety nets read, from the solution runs.

    cd labs
    uv run python prepare_data.py
    uv run python _tools/make_reference.py      # runs every solution source, then copies its outputs

Each solution source is run as a script (quick mode off), then the outputs listed in COPY are copied
from labs/artifacts/ to labs/data/reference/. The generator's own reference files are not touched.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
COPY = {
    "D1_2_write_definitions_rules": [("d1_2/guideline_v1_0.json", "guideline_v1_0.json")],
    "D1_3_compute_kappa_alpha": [("d1_3/agreement_round1.json", "d1_3_agreement.json")],
    "D1_4_adjudicate_30_disagreements": [("d1_4/guideline_v1_1.json", "guideline_v1_1.json"), ("d1_4/agreement_r1_r2.csv", "agreement_r1_r2.csv")],
    "D2_1_draw_stratified_golden": [("d2_1/coverage.json", "d2_1_coverage.json")],
    "D2_2_set_gold_question": [("d2_2/routing.json", "d2_2_routing.json")],
    "D2_3_find_drifting_rater": [("d2_3/drift.json", "d2_3_drift.json")],
    "D2_4_compare_cost_per": [("d2_4/designs.json", "d2_4_designs.json")],
    "D3_1_profile_four_source": [("d3_1/profile.json", "d3_1_profile.json")],
    "D3_2_implement_warning_blocking": [("d3_2/rule_results.json", "d3_2_rule_results.json")],
    "D3_3_match_merchant_names": [("d3_3/matches.csv", "d3_3_matches.csv"), ("d3_3/curve.json", "d3_3_curve.json")],
    "D3_4_write_contract_prepared": [("d3_4/contract.odcs.yaml", "contract.odcs.yaml")],
    "D4_4_write_preparation_section": [],
}

if __name__ == "__main__":
    only = sys.argv[1:]
    env = dict(os.environ, DS311_QUICK="0", PYTHONIOENCODING="utf-8")
    for src, files in COPY.items():
        if only and src not in only:
            continue
        print("running", src)
        subprocess.run([sys.executable, str(LABS / "_src" / f"{src}.py")], cwd=LABS, env=env, check=True, stdout=subprocess.DEVNULL)
        for a, b in files:
            shutil.copyfile(LABS / "artifacts" / a, LABS / "data" / "reference" / b)
            print("  wrote data/reference/" + b)
