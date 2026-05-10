"""
File: _test_extract.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
Baseline OSM 추출과 neutral 변수 적용 파이프라인을 빠르게 점검한다.

======================================================================
Description:
baseline OSM에서 calibration 파라미터를 추출하고 JSON으로 저장한 뒤 다시 로드하여,
neutral Optuna 변수와 일부 시험값을 적용할 수 있는지 확인하는 스모크 테스트 스크립트다.

Input:
- baseline OSM 파일
- Optuna search space 정의

Output:
- baseline params JSON
- 테스트용 적용 OSM
- 콘솔 검증 로그

======================================================================
Note:
주 실행 파이프라인이 아니라 추출/적용 기능 점검용 보조 스크립트다.

======================================================================
Run:
python materials/code/_test_extract.py

"""
from pathlib import Path
import json

_WIN_USER = next((n for n in ("ryudo", "USER") if Path(f"/mnt/c/Users/{n}").exists()), "ryudo")

from osm_calibration_params import (
    extract_baseline_params, save_params, load_params, default_output_path,
)
from optuna_search_space import OPTUNA_SEARCH_SPACE, neutral_values
from apply_calibrated_vars import apply_optuna_vars, compute_applied_summary, write_applied_to_osm


BUILDING_NAME = "KETI_jb"
OSM_IN   = Path(f"/mnt/c/Users/{_WIN_USER}/OneDrive - gachon.ac.kr/2-stage_osm_calibration-osm/osm/baseline_osm_20260503_2010.osm")
OSM_OUT  = Path(f"/mnt/c/Users/{_WIN_USER}/OneDrive - gachon.ac.kr/2-stage_osm_calibration/materials/optuna/trial_test.osm")
JSON_OUT = default_output_path(BUILDING_NAME)   # materials/building_params/KETI_jb_params.json


def main():
    print(f"[1/5] Extract: {OSM_IN.name}")
    params = extract_baseline_params(OSM_IN)
    print(f"      metadata: {params['metadata']}")
    n_zones = params["metadata"]["n_zones"]
    n_st = params["metadata"]["n_space_types"]
    print(f"      candidates keys: {list(params['candidates'])}")
    print(f"      context keys: {list(params['context'])}")

    print(f"[2/5] Save JSON")
    save_params(params, JSON_OUT)
    size_kb = JSON_OUT.stat().st_size / 1024
    print(f"      → {JSON_OUT}  ({size_kb:.1f} KB)")

    print(f"[3/5] Load JSON back + verify")
    reloaded = load_params(JSON_OUT)
    assert reloaded["metadata"]["n_zones"] == n_zones
    assert reloaded["metadata"]["n_space_types"] == n_st
    print(f"      reload OK")

    print(f"[4/5] Apply trial vars (dict): equipment_multiplier=1.2, heating_offset=+1.5")
    trial = {**neutral_values(), "equipment_multiplier": 1.2, "heating_setpoint_offset": 1.5}
    applied = apply_optuna_vars(params, trial)
    print(f"      applied keys: {list(applied['candidates'])}")
    summary = compute_applied_summary(applied)
    print(f"      summary: extreme_setpoint={len(summary['extreme_setpoint'])}, "
          f"efficiency_clipped={len(summary['efficiency_clipped'])}")
    sample_target = applied["candidates"]["equipment_multiplier"]["targets"][0]
    print(f"      sample equipment apply: {sample_target.get('object_name')}: "
          f"{sample_target.get('baseline_value')} → {sample_target.get('applied_value')}")

    print(f"[5/5] Write to OSM")
    result = write_applied_to_osm(applied, OSM_IN, OSM_OUT)
    print(f"      → {OSM_OUT}")
    print(f"      objects modified: {result['objects_modified']}")

    print()
    print("ALL PASS")


if __name__ == "__main__":
    main()
