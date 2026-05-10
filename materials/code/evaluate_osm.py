"""
File: evaluate_osm.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
단일 OSM 모델의 시뮬레이션 결과를 실측 데이터와 비교 평가한다.

======================================================================
Description:
입력 OSM과 EPW로 시뮬레이션을 수행하고 월별 전기 및 가스 사용량을 추출한 뒤,
CVRMSE, NMBE, 목적함수 J를 계산한다. Optuna 전체 루프 없이 개별 OSM 성능을 점검할 때 사용한다.

Input:
- 평가 대상 OSM 파일
- EPW 파일
- 실측 전기 CSV
- 실측 가스 CSV

Output:
- 평가 결과 JSON
- 성능 요약 정보
- 평가 실행 폴더

======================================================================
Note:
특정 trial OSM이나 baseline OSM을 독립적으로 검증할 때 유용하다.

======================================================================
Run:
python materials/code/evaluate_osm.py --help

"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from score import DEFAULT_MEASURED_ELEC, DEFAULT_MEASURED_GAS, compute_score
from simulation import extract_monthly_results, simulate_and_extract


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EPW = PROJECT_ROOT / "raw" / "KOR_CB_Jeonju.471460_TMYx.2011-2025.epw"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "materials" / "evaluation_runs"


def resolve_path(path_str: str) -> Path:
    """Convert Windows paths to WSL paths and normalize separators."""
    if len(path_str) >= 3 and path_str[1:3] == ":\\":
        drive = path_str[0].lower()
        suffix = path_str[3:].replace("\\", "/")
        return Path(f"/mnt/{drive}/{suffix}")
    return Path(path_str.replace("\\", "/"))


DEFAULT_OSM_DIR = resolve_path(
    r"C:\Users\ryudo\OneDrive - gachon.ac.kr\2-stage_osm_calibration-osm\osm"
)


def build_summary(score_payload: dict[str, Any]) -> dict[str, Any]:
    metrics = score_payload["metrics"]
    return {
        "J": score_payload["J"],
        "cvrmse_elec": metrics["cvrmse_elec"],
        "cvrmse_gas": metrics["cvrmse_gas"],
        "nmbe_elec": metrics["nmbe_elec"],
        "nmbe_gas": metrics["nmbe_gas"],
        "annual_error_elec_pct": metrics["annual_error_elec_pct"],
        "annual_error_gas_pct": metrics["annual_error_gas_pct"],
        "annual_abs_error_elec_pct": metrics["annual_abs_error_elec_pct"],
        "annual_abs_error_gas_pct": metrics["annual_abs_error_gas_pct"],
        "ashrae_g14": score_payload["ashrae_g14"],
        "warnings": score_payload["warnings"],
    }


def find_default_osm() -> Path:
    if not DEFAULT_OSM_DIR.exists():
        raise FileNotFoundError(f"기본 OSM 폴더를 찾을 수 없습니다: {DEFAULT_OSM_DIR}")
    candidates = sorted(
        DEFAULT_OSM_DIR.glob("*.osm"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"기본 OSM 폴더에 .osm 파일이 없습니다: {DEFAULT_OSM_DIR}")
    return candidates[0]


def resolve_osm_input(osm_arg: str | None) -> Path:
    if not osm_arg:
        return find_default_osm()

    candidate = resolve_path(osm_arg)
    if candidate.exists():
        return candidate

    raw = osm_arg.replace("\\", "/")
    if "/" not in raw:
        default_candidate = DEFAULT_OSM_DIR / raw
        if default_candidate.exists():
            return default_candidate

    return candidate


def find_latest_simulation_dir(osm_path: Path) -> Path | None:
    pattern = f"{osm_path.stem}_*"
    candidates = [
        p for p in DEFAULT_OUTPUT_ROOT.glob(pattern)
        if p.is_dir() and (p / "run" / "eplusout.sql").exists()
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def find_neighbor_simulation_dir(osm_path: Path) -> Path | None:
    candidate = osm_path.parent / osm_path.stem
    sql_in_run = candidate / "run" / "eplusout.sql"
    sql_direct = candidate / "eplusout.sql"
    if sql_in_run.exists() or sql_direct.exists():
        return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run one OSM and compare monthly results against measured data."
    )
    parser.add_argument(
        "--osm",
        help=(
            "평가할 OSM 경로. 생략 시 "
            f"{DEFAULT_OSM_DIR} 폴더의 최신 .osm 사용"
        ),
    )
    parser.add_argument("--epw", default=str(DEFAULT_EPW), help="EPW 경로")
    parser.add_argument(
        "--out",
        help="시뮬레이션/평가 출력 디렉터리. 기본값: materials/evaluation_runs/<osm_stem>_<timestamp>",
    )
    parser.add_argument(
        "--measured-elec", default=str(DEFAULT_MEASURED_ELEC), help="전력 실측 CSV"
    )
    parser.add_argument(
        "--measured-gas", default=str(DEFAULT_MEASURED_GAS), help="가스 실측 CSV"
    )
    parser.add_argument(
        "--openstudio-bin", default="openstudio", help="OpenStudio CLI 경로 또는 명령어"
    )
    parser.add_argument("--timeout", type=int, default=1800, help="시뮬레이션 제한시간(초)")
    parser.add_argument(
        "--simulation-dir",
        help="기존 시뮬레이션 결과 폴더. 지정 시 재시뮬레이션 없이 <dir>/run/eplusout.sql 사용",
    )
    parser.add_argument(
        "--results-only",
        action="store_true",
        help="재시뮬레이션 없이 기존 결과만 사용. --simulation-dir 없으면 같은 OSM 이름의 최신 결과 폴더 자동 탐색",
    )
    parser.add_argument(
        "--out-json",
        help="평가 결과 JSON 저장 경로. 기본값: <out>/evaluation.json",
    )
    args = parser.parse_args()

    osm_path = resolve_osm_input(args.osm)
    epw_path = resolve_path(args.epw)
    measured_elec = resolve_path(args.measured_elec)
    measured_gas = resolve_path(args.measured_gas)

    if args.out:
        out_dir = resolve_path(args.out)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = DEFAULT_OUTPUT_ROOT / f"{osm_path.stem}_{stamp}"

    if args.simulation_dir:
        run_source_dir = resolve_path(args.simulation_dir)
    elif (found := find_neighbor_simulation_dir(osm_path)) is not None:
        run_source_dir = found
    elif args.results_only:
        found = find_latest_simulation_dir(osm_path)
        if found is None:
            raise FileNotFoundError(
                f"기존 시뮬레이션 결과를 찾지 못했습니다: stem={osm_path.stem}"
            )
        run_source_dir = found
    else:
        run_source_dir = None

    if run_source_dir is not None:
        sql_path = run_source_dir / "run" / "eplusout.sql"
        if not sql_path.exists():
            sql_path = run_source_dir / "eplusout.sql"
        if not sql_path.exists():
            raise FileNotFoundError(f"eplusout.sql을 찾을 수 없습니다: {run_source_dir}")
        out_dir = run_source_dir
        sim_payload = {
            "simulation": {
                "osm_path": str(osm_path),
                "epw_path": str(epw_path),
                "osw_path": None,
                "run_dir": str(run_source_dir / "run"),
                "sql_path": str(sql_path),
                "openstudio_bin": None,
                "status": "skipped_existing_results",
                "returncode": 0,
                "stdout_tail": "",
                "stderr_tail": "",
            },
            "results": extract_monthly_results(sql_path),
        }
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        sim_payload = simulate_and_extract(
            osm_path=osm_path,
            epw_path=epw_path,
            output_dir=out_dir,
            openstudio_bin=args.openstudio_bin,
            ensure_meters=True,
            timeout_sec=args.timeout,
        )
        if sim_payload["simulation"]["status"] != "success" or sim_payload["results"] is None:
            raise RuntimeError(
                "시뮬레이션 실패: "
                + json.dumps(sim_payload["simulation"], ensure_ascii=False, indent=2)
            )

    score_payload = compute_score(
        sim_payload["results"],
        measured_elec_path=measured_elec,
        measured_gas_path=measured_gas,
    )

    payload = {
        "inputs": {
            "osm": str(osm_path),
            "epw": str(epw_path),
            "measured_elec": str(measured_elec),
            "measured_gas": str(measured_gas),
        },
        "simulation": sim_payload["simulation"],
        "results": sim_payload["results"],
        "score": score_payload,
        "summary": build_summary(score_payload),
    }

    out_json = resolve_path(args.out_json) if args.out_json else out_dir / "evaluation.json"
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    print(f"saved_json: {out_json}")
    print(f"run_dir: {out_dir}")


if __name__ == "__main__":
    main()
