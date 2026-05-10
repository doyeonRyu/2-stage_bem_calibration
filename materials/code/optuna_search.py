"""
File: optuna_search.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
Stage 1 calibration을 위한 iterative joint Optuna search를 수행한다.

======================================================================
Description:
baseline OSM, baseline params, EPW, 실측 데이터 입력을 기반으로 Optuna(TPE) trial을
라운드 단위로 반복 실행한다. 각 trial에서 변수 샘플링, OSM 반영, 시뮬레이션, 점수 계산을 수행하고,
라운드 종료 시 freeze 판정과 search space 축소를 적용한다.

1. 입력 로드 
- baseline OSM
- baseline params JSON (calibration 대상 변수 후보 + literature bounds)
- EPW
- 실측 전기/가스 데이터

2. 활성 변수 초기화 
- optuna_search_space.py에서 enabled=True인 7개 변수만 active로 가져옴
- 초기 current_best는 neutral 값으로 시작
- 초기 alpha도 변수별로 설정

3. 각 round 시작
- 현재 current_best와 alpha를 기준으로 round용 search space 구성
- Round 1은 literature range 그대로 사용
- Round 2부터는 best ± alpha 범위로 줄여서 사용

4. 각 trial 반복
- Optuna가 round search space 안에서 변수값 샘플링
- 샘플링된 변수값을 apply_calibrated_vars.py로 baseline OSM에 반영
- simulation.py로 시뮬레이션 실행
- score.py로 J, CVRMSE, NMBE 계산
- Optuna가 그 trial 결과를 저장

5. round 종료 후 best trial 선택
- 그 round의 best trial 변수값을 가져옴
- 이전 round 대비 개선 여부 확인
- 개선되면 current_best 갱신
- 변화가 작은 변수는 freeze 후보로 누적
- freeze 안 된 변수는 다음 round에서 alpha *= rho로 search space 축소

6. 종료 조건 확인
- 개선 정체 2회 연속
- 모든 active 변수 freeze
- r_max 도달
- 이 중 하나면 종료

Input:
- baseline OSM 파일
- baseline params JSON
- EPW 파일
- 실측 전기 CSV
- 실측 가스 CSV
- 라운드 및 trial 하이퍼파라미터

Output:
- trial별 산출물 디렉터리
- Optuna study DB
- 라운드 요약 JSON
- 최종 summary JSON

======================================================================
Note:
현재 Stage 1 1차 운영 범위에서는 `optuna_search_space.py`의 `enabled=True` 7개 변수만 활성화된다.

======================================================================
Run:
python materials/code/optuna_search.py --help

"""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import optuna

from osm_calibration_params import load_params
from optuna_search_space import (
    OPTUNA_SEARCH_SPACE,
    get_enabled_vars,
    neutral_values,
)
from apply_calibrated_vars import apply_optuna_vars, write_applied_to_osm
from simulation import simulate_and_extract
from score import (
    compute_score,
    DEFAULT_MEASURED_ELEC,
    DEFAULT_MEASURED_GAS,
)


# ---------------------------------------------------------------------------
# Defaults (paper §3 Inter-round Orchestration Protocol + 1차 운영 범위)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]   # materials/

def _detect_win_user() -> str:
    """두 대의 PC에서 Windows 사용자 폴더를 자동 감지 (ryudo → USER 순)."""
    for name in ("ryudo", "USER"):
        if Path(f"/mnt/c/Users/{name}").exists():
            return name
    return "ryudo"

_WIN_USER = _detect_win_user()

DEFAULT_BASELINE_OSM = Path(
    f"/mnt/c/Users/{_WIN_USER}/OneDrive - gachon.ac.kr/2-stage_osm_calibration-osm/osm/baseline_osm_20260503_2213.osm"
)
# Note: openstudio Python이 E: 경로 OSM을 못 읽는 환경 이슈 → baseline은 C:에서 로드.
# trial 출력은 여전히 E:\...\materials\optuna\trials\ 시도 (write가 작동하면 그대로,
# 안 되면 trials_root를 C: 비-OneDrive 경로로 전환 필요).
DEFAULT_BASELINE_PARAMS = PROJECT_ROOT / "building_params" / "KETI_jb_params.json"
DEFAULT_EPW = Path(
    f"/mnt/c/Users/{_WIN_USER}/OneDrive - gachon.ac.kr/2-stage_osm_calibration-osm/KOR_CB_Jeonju.471460_TMYx.2011-2025.epw"
)

# 무거운 trial OSM/run/은 openstudio Python이 E:에 write 불가 → C: 비-OneDrive 경로.
# 가벼운 sqlite DB (Optuna)와 요약 JSON은 Python이 직접 쓰므로 E: 가능 (논문 repo 안).
DEFAULT_TRIALS_ROOT    = Path(f"/mnt/c/Users/{_WIN_USER}/optuna_trials")
DEFAULT_STUDIES_ROOT   = PROJECT_ROOT / "optuna" / "studies"
DEFAULT_SUMMARIES_ROOT = PROJECT_ROOT / "optuna" / "summaries"

DEFAULT_STUDY_NAME = "KETI_jb_phase1"

# Protocol thresholds
DEFAULT_N_TRIAL      = 10
DEFAULT_R_MAX        = 7
DEFAULT_RHO          = 0.7
DEFAULT_THETA_J      = 0.01    # 1% J 개선 미만 → 정체 카운트 증가
DEFAULT_THETA_FREEZE = 0.05    # 5% (multiplier 변수)
DEFAULT_THERMOSTAT_MIN_GAP = 1.0  # °C, adjusted heating/cooling occupied gap

# offset/shift 변수 freeze 절대값 임계 (multiplier rel%로 환산 어려움)
FREEZE_ABS_OFFSET = 0.1   # °C 또는 hour 미만이면 stable
FREEZE_ABS_SHIFT  = 1     # int hour

# 트라이얼 실패 시 부여할 큰 J (Optuna가 회피 학습)
FAILURE_J = 1.0e6


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
def _normalize_path(path_like: Path | str) -> Path:
    """Accept native or Windows-style paths when running under WSL/Linux."""
    raw = str(path_like)
    win_drive = re.match(r"^([A-Za-z]):[\\/](.*)$", raw)
    if win_drive:
        drive = win_drive.group(1).lower()
        rest = win_drive.group(2).replace("\\", "/")
        return Path(f"/mnt/{drive}/{rest}")
    return Path(raw)


def _trial_log(trial_num: int, message: str) -> None:
    print(f"[trial {trial_num:03d}] {message}", flush=True)


# ---------------------------------------------------------------------------
# Helpers — variable typing / freeze
# ---------------------------------------------------------------------------
def _is_offset_var(name: str) -> bool:
    return "offset" in name


def _is_shift_var(name: str) -> bool:
    return "shift" in name


def _is_int_var(entry: dict) -> bool:
    return entry.get("type") == "int"


def check_freeze(prev: float, curr: float, name: str, theta_freeze: float) -> bool:
    """한 라운드 변수 변동이 freeze 임계 미만인지.

    - offset 변수: |curr - prev| < FREEZE_ABS_OFFSET
    - shift 변수: |curr - prev| < FREEZE_ABS_SHIFT
    - multiplier 변수: |curr - prev| / max(|prev|, 1e-9) < theta_freeze
    """
    delta = abs(curr - prev)
    if _is_offset_var(name):
        return delta < FREEZE_ABS_OFFSET
    if _is_shift_var(name):
        return delta < FREEZE_ABS_SHIFT
    denom = max(abs(prev), 1e-9)
    return (delta / denom) < theta_freeze


# ---------------------------------------------------------------------------
# Search space builder
# ---------------------------------------------------------------------------
def build_round_search_space(
    active_vars: dict[str, dict],
    current_best: dict[str, float],
    alpha_per_var: dict[str, float],
    round_num: int,
) -> dict[str, dict]:
    """라운드 시작 시 변수별 (low, high) 결정.

    Round 1: OPTUNA_SEARCH_SPACE의 literature range 그대로 사용.
    Round 2+: clamp(best ± alpha) within literature bounds.
    """
    space: dict[str, dict] = {}
    for name, entry in active_vars.items():
        full_low = float(entry["low"])
        full_high = float(entry["high"])
        if round_num == 1:
            lo, hi = full_low, full_high
        else:
            best = float(current_best.get(name, (full_low + full_high) / 2))
            alpha = float(alpha_per_var.get(name, (full_high - full_low) / 2))
            lo = max(full_low, best - alpha)
            hi = min(full_high, best + alpha)
            if lo >= hi:
                # 안전망: 너무 좁으면 ±2α로 확장 (alpha 경계 도달 1회 확장 규칙)
                lo = max(full_low, best - 2 * alpha)
                hi = min(full_high, best + 2 * alpha)
            if lo >= hi:
                # 그래도 같으면 literature 폭 1%
                pad = (full_high - full_low) * 0.005
                lo = max(full_low, best - pad)
                hi = min(full_high, best + pad)
        space[name] = {**entry, "low": lo, "high": hi}
    return space


def _initial_alpha(entry: dict) -> float:
    """변수별 alpha 초기값: literature range 절반."""
    return (float(entry["high"]) - float(entry["low"])) / 2.0


def _suggest_value(trial: optuna.Trial, name: str, spec: dict) -> float:
    """Optuna trial.suggest_*. spec는 {low, high, type, step?}."""
    if _is_int_var(spec):
        step = int(spec.get("step", 1))
        return trial.suggest_int(name, int(spec["low"]), int(spec["high"]), step=step)
    step = spec.get("step")
    if step is None:
        return trial.suggest_float(name, float(spec["low"]), float(spec["high"]))
    return trial.suggest_float(
        name, float(spec["low"]), float(spec["high"]), step=float(step)
    )


def _required_cooling_offset_delta(baseline_dict: dict[str, Any], min_gap: float) -> float:
    """Return the minimum offset delta needed to keep cooling >= heating + min_gap.

    The constraint is computed over thermostat targets that are actually adjustable in
    Stage 1. Zones with baseline deadband below the protection threshold are already
    skipped downstream and are excluded here as well.
    """
    thermostat_targets = (
        baseline_dict.get("candidates", {})
        .get("heating_setpoint_offset", {})
        .get("targets", [])
    )
    required_delta = 0.0
    for target in thermostat_targets:
        h_occ = target.get("htg_occupied")
        c_occ = target.get("clg_occupied")
        if h_occ is None or c_occ is None:
            continue
        baseline_gap = float(c_occ) - float(h_occ)
        if baseline_gap < DEFAULT_THERMOSTAT_MIN_GAP:
            continue
        required_delta = max(required_delta, min_gap - baseline_gap)
    return required_delta


def _sample_round_variables(
    trial: optuna.Trial,
    round_search_space: dict[str, dict],
    baseline_dict: dict[str, Any],
    thermostat_min_gap: float,
) -> dict[str, float]:
    """Sample trial variables, enforcing thermostat min-gap by joint parameterization."""
    sampled: dict[str, float] = {}
    thermostat_pair = {
        "heating_setpoint_offset",
        "cooling_setpoint_offset",
    }
    has_thermostat_pair = thermostat_pair.issubset(round_search_space)

    if has_thermostat_pair:
        h_spec = round_search_space["heating_setpoint_offset"]
        c_spec = round_search_space["cooling_setpoint_offset"]
        required_delta = _required_cooling_offset_delta(baseline_dict, thermostat_min_gap)

        h_low = float(h_spec["low"])
        h_high = float(h_spec["high"])
        c_low = float(c_spec["low"])
        c_high = float(c_spec["high"])

        feasible_h_high = min(h_high, c_high - required_delta)
        if feasible_h_high < h_low:
            raise ValueError(
                "Infeasible thermostat search space: heating offset range and cooling "
                f"offset range cannot satisfy min_gap={thermostat_min_gap}°C."
            )

        sampled["heating_setpoint_offset"] = _suggest_value(
            trial,
            "heating_setpoint_offset",
            {**h_spec, "low": h_low, "high": feasible_h_high},
        )

        feasible_c_low = max(c_low, sampled["heating_setpoint_offset"] + required_delta)
        if feasible_c_low > c_high:
            raise ValueError(
                "Infeasible sampled thermostat trial: cooling offset lower bound exceeds "
                f"its upper bound under min_gap={thermostat_min_gap}°C."
            )

        sampled["cooling_setpoint_offset"] = _suggest_value(
            trial,
            "cooling_setpoint_offset",
            {**c_spec, "low": feasible_c_low, "high": c_high},
        )

    for name, spec in round_search_space.items():
        if name in sampled:
            continue
        sampled[name] = _suggest_value(trial, name, spec)

    return sampled


# ---------------------------------------------------------------------------
# Trial objective factory
# ---------------------------------------------------------------------------
def make_objective(
    *,
    baseline_dict: dict,
    baseline_osm: Path,
    epw: Path,
    measured_elec: Path,
    measured_gas: Path,
    weights: dict[str, float] | None,
    round_dir: Path,
    round_search_space: dict[str, dict],
    frozen_vars: dict[str, float],
    thermostat_min_gap: float,
):
    """Optuna objective closure. trial → J."""

    def objective(trial: optuna.Trial) -> float:
        trial_dir = round_dir / f"trial_{trial.number:03d}"
        trial_dir.mkdir(parents=True, exist_ok=True)
        trial_osm = trial_dir / "trial.osm"
        case_json = trial_dir / "case.json"
        score_json = trial_dir / "score.json"
        run_dir = trial_dir / "run"

        # 1. 변수 sampling: active 변수만 trial.suggest, 나머지는 frozen 또는 neutral
        _trial_log(trial.number, "sampling variables...")
        sampled = _sample_round_variables(
            trial,
            round_search_space,
            baseline_dict,
            thermostat_min_gap,
        )
        _trial_log(trial.number, f"sampled: {sampled}")

        variables: dict[str, float] = {**neutral_values(), **frozen_vars, **sampled}

        # 2. 변수 적용 → trial OSM 작성
        try:
            _trial_log(trial.number, "applying variables to OSM...")
            applied = apply_optuna_vars(baseline_dict, variables)
            write_summary = write_applied_to_osm(applied, baseline_osm, trial_osm)
            _trial_log(trial.number, f"trial OSM written: {trial_osm}")
        except Exception as exc:
            _trial_log(trial.number, f"apply failed: {exc}")
            _save_failed_trial(
                trial_dir, case_json, score_json, sampled, variables, frozen_vars,
                stage="apply", error=str(exc), tb=traceback.format_exc(),
            )
            return FAILURE_J

        # 3. 시뮬레이션 + 결과 추출
        try:
            _trial_log(trial.number, "running simulation...")
            sim_payload = simulate_and_extract(
                osm_path=trial_osm,
                epw_path=epw,
                output_dir=trial_dir,        # workflow.osw + run/ 모두 trial_dir 안에
                ensure_meters=False,         # baseline에 이미 추가됨
            )
            _trial_log(
                trial.number,
                f"simulation status: {sim_payload['simulation']['status']}"
            )
        except Exception as exc:
            _trial_log(trial.number, f"simulation failed: {exc}")
            _save_failed_trial(
                trial_dir, case_json, score_json, sampled, variables, frozen_vars,
                stage="simulate", error=str(exc), tb=traceback.format_exc(),
            )
            return FAILURE_J

        if sim_payload["simulation"]["status"] != "success" or sim_payload["results"] is None:
            _trial_log(
                trial.number,
                "simulation returned non-success status; assigning failure penalty."
            )
            _save_failed_trial(
                trial_dir, case_json, score_json, sampled, variables, frozen_vars,
                stage="simulate", error="status != success",
                sim_summary=sim_payload["simulation"],
            )
            return FAILURE_J

        # 4. score
        try:
            _trial_log(trial.number, "computing score...")
            score = compute_score(
                sim_payload["results"],
                measured_elec_path=measured_elec,
                measured_gas_path=measured_gas,
                weights=weights,
            )
        except Exception as exc:
            _trial_log(trial.number, f"score failed: {exc}")
            _save_failed_trial(
                trial_dir, case_json, score_json, sampled, variables, frozen_vars,
                stage="score", error=str(exc), tb=traceback.format_exc(),
                sim_summary=sim_payload["simulation"],
            )
            return FAILURE_J

        J = score["J"]
        if math.isnan(J) or math.isinf(J):
            J = FAILURE_J
        _trial_log(trial.number, f"score complete: J={J:.4f}")

        # 5. 산출물 저장
        case_json.write_text(
            json.dumps({
                "trial_number":   trial.number,
                "sampled":        sampled,
                "frozen_vars":    frozen_vars,
                "all_variables":  variables,
                "trial_osm":      str(trial_osm),
                "write_summary":  write_summary,
            }, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        score_json.write_text(
            json.dumps(score, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        trial.set_user_attr("J", J)
        trial.set_user_attr("metrics", score["metrics"])
        trial.set_user_attr("ashrae_g14", score["ashrae_g14"])
        trial.set_user_attr("trial_dir", str(trial_dir))
        _trial_log(trial.number, "trial finished.")
        return J

    return objective


def _save_failed_trial(
    trial_dir: Path, case_json: Path, score_json: Path,
    sampled: dict, variables: dict, frozen_vars: dict,
    *, stage: str, error: str,
    tb: str | None = None,
    sim_summary: dict | None = None,
) -> None:
    """trial 실패 시 case/score 자리표시자 작성."""
    case_json.write_text(
        json.dumps({
            "sampled":     sampled,
            "frozen_vars": frozen_vars,
            "all_variables": variables,
            "failed":      True,
            "stage":       stage,
            "error":       error,
            "traceback":   tb,
            "sim_summary": sim_summary,
        }, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    score_json.write_text(
        json.dumps({
            "failed": True,
            "stage":  stage,
            "error":  error,
            "J":      FAILURE_J,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Round driver
# ---------------------------------------------------------------------------
def run_round(
    *,
    study_storage: str,
    study_name_round: str,
    n_trial: int,
    objective_fn,
    enqueue: dict | None = None,
) -> optuna.Study:
    """라운드별 Optuna study 생성 + 실행. 이전 best을 enqueue로 warm-start."""
    sampler = optuna.samplers.TPESampler(seed=None)
    study = optuna.create_study(
        study_name=study_name_round,
        storage=study_storage,
        sampler=sampler,
        direction="minimize",
        load_if_exists=True,
    )
    if enqueue:
        # 라운드 첫 trial에 이전 best을 강제 sample (warm start)
        study.enqueue_trial(enqueue)
    study.optimize(objective_fn, n_trials=n_trial, gc_after_trial=True)
    return study


# ---------------------------------------------------------------------------
# Top-level orchestrator
# ---------------------------------------------------------------------------
def run_phase1(args: argparse.Namespace) -> dict[str, Any]:
    """라운드 반복 실행 + freeze 추적 + 종료 조건 평가."""
    started = datetime.now()
    timestamp = started.strftime("%Y%m%d_%H%M")
    run_name = f"{args.study_name}_{timestamp}"

    # 입력 자산 로드/검증
    baseline_osm = _normalize_path(args.baseline_osm).resolve()
    baseline_params = _normalize_path(args.baseline_params).resolve()
    epw = _normalize_path(args.epw).resolve()
    measured_elec = _normalize_path(args.measured_elec).resolve()
    measured_gas = _normalize_path(args.measured_gas).resolve()
    for p in (baseline_osm, baseline_params, epw, measured_elec, measured_gas):
        if not p.exists():
            raise FileNotFoundError(f"Required input not found: {p}")

    baseline_dict = load_params(baseline_params)

    # Output dirs
    trials_root    = _normalize_path(args.trials_root).resolve()
    studies_root   = _normalize_path(args.studies_root).resolve()
    summaries_root = _normalize_path(args.summaries_root).resolve()
    run_root = trials_root / run_name
    run_root.mkdir(parents=True, exist_ok=True)
    studies_root.mkdir(parents=True, exist_ok=True)
    summaries_root.mkdir(parents=True, exist_ok=True)

    # Optuna SQLite storage (한 study 파일에 round별 sub-study 다 저장)
    db_path = studies_root / f"{run_name}.db"
    study_storage = f"sqlite:///{db_path.as_posix()}"

    # 변수 초기화
    active_vars = get_enabled_vars()         # 7 vars (1차 운영 범위)
    initial_neutral = neutral_values()
    current_best: dict[str, float] = {n: initial_neutral[n] for n in active_vars}
    alpha_per_var: dict[str, float] = {n: _initial_alpha(e) for n, e in active_vars.items()}
    frozen_vars: dict[str, float] = {}       # name → frozen value
    stable_count: dict[str, int] = {n: 0 for n in active_vars}  # 연속 stable 라운드 수
    J_history: list[float] = []
    stagnant_count = 0
    rounds_summary: list[dict] = []

    # Round 0 baseline J (active 변수 모두 neutral)
    print(f"[run_phase1] Run name: {run_name}")
    print(f"[run_phase1] Active vars ({len(active_vars)}): {list(active_vars.keys())}")

    # Round loop
    stop_reason = "r_max"
    for round_num in range(1, args.r_max + 1):
        round_dir = run_root / f"round_{round_num}"
        round_dir.mkdir(parents=True, exist_ok=True)

        # Active = 전체 active_vars - frozen
        round_active = {n: e for n, e in active_vars.items() if n not in frozen_vars}
        if not round_active:
            stop_reason = "freeze_complete"
            print(f"[round {round_num}] 모든 active 변수가 freeze. 종료.")
            break

        round_search_space = build_round_search_space(
            round_active, current_best, alpha_per_var, round_num
        )

        # warm start: 라운드 2+ 에서 이전 best을 trial 0으로 강제
        warm_start = None
        if round_num > 1:
            warm_start = {n: current_best[n] for n in round_active}

        objective_fn = make_objective(
            baseline_dict=baseline_dict,
            baseline_osm=baseline_osm,
            epw=epw,
            measured_elec=measured_elec,
            measured_gas=measured_gas,
            weights=None,
            round_dir=round_dir,
            round_search_space=round_search_space,
            frozen_vars=frozen_vars,
            thermostat_min_gap=DEFAULT_THERMOSTAT_MIN_GAP,
        )

        round_t0 = time.time()
        print(
            f"\n[round {round_num}] active={list(round_active)} "
            f"frozen={list(frozen_vars)} alpha={ {k: round(v, 3) for k, v in alpha_per_var.items() if k in round_active} }"
        )
        study = run_round(
            study_storage=study_storage,
            study_name_round=f"{run_name}__round_{round_num}",
            n_trial=args.n_trial,
            objective_fn=objective_fn,
            enqueue=warm_start,
        )
        round_dur = time.time() - round_t0

        # 라운드 결과
        best_trial = study.best_trial
        J_round = float(best_trial.value)
        best_params_round = dict(best_trial.params)

        # full best variables (frozen 포함, sampled 외는 neutral)
        full_best = {**neutral_values(), **frozen_vars, **best_params_round}

        # 개선 여부 판정
        improved = (not J_history) or (J_round < J_history[-1])
        if improved:
            # freeze 판정: 라운드 best vs 직전 current_best 비교
            for name in list(round_active):
                prev_v = current_best[name]
                curr_v = best_params_round.get(name, prev_v)
                if check_freeze(prev_v, curr_v, name, args.theta_freeze):
                    stable_count[name] += 1
                    if stable_count[name] >= 2:
                        frozen_vars[name] = curr_v
                else:
                    stable_count[name] = 0
            # search space 축소
            for name in list(round_active):
                if name not in frozen_vars:
                    alpha_per_var[name] *= args.rho
            # current_best 갱신
            for name, v in best_params_round.items():
                current_best[name] = v

            # stagnant 카운트
            if J_history:
                rel = (J_history[-1] - J_round) / max(abs(J_history[-1]), 1e-9)
                if rel < args.theta_J:
                    stagnant_count += 1
                else:
                    stagnant_count = 0
            J_history.append(J_round)
        else:
            # J 악화: best-so-far 유지, freeze 갱신 건너뜀
            stagnant_count += 1
            J_history.append(J_history[-1])
            print(f"[round {round_num}] J 악화 ({J_round:.4f} >= prev {J_history[-2]:.4f}). best-so-far 유지.")

        # 라운드 요약 저장
        round_summary = {
            "round_num":       round_num,
            "study_name":      f"{run_name}__round_{round_num}",
            "round_dir":       str(round_dir),
            "active_vars":     list(round_active),
            "frozen_vars":     dict(frozen_vars),
            "alpha_per_var":   {k: float(v) for k, v in alpha_per_var.items() if k in round_active},
            "search_space":    {k: {"low": float(s["low"]), "high": float(s["high"])}
                                for k, s in round_search_space.items()},
            "n_trial":         args.n_trial,
            "best_J":          J_round,
            "best_params":     best_params_round,
            "full_best":       full_best,
            "improved":        improved,
            "stable_count":    dict(stable_count),
            "stagnant_count":  stagnant_count,
            "duration_sec":    round_dur,
            "trial_records":   [
                {
                    "number": t.number,
                    "value":  t.value,
                    "params": t.params,
                    "state":  t.state.name,
                }
                for t in study.trials
            ],
        }
        rounds_summary.append(round_summary)
        (round_dir / "round_summary.json").write_text(
            json.dumps(round_summary, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(
            f"[round {round_num}] best_J={J_round:.4f} "
            f"frozen={len(frozen_vars)}/{len(active_vars)} "
            f"stagnant={stagnant_count} dur={round_dur:.1f}s"
        )

        # 종료 조건
        if stagnant_count >= 2:
            stop_reason = "convergence"
            print(f"[round {round_num}] θ_J 정체 2회 연속 → 수렴 종료.")
            break
        if len(frozen_vars) == len(active_vars):
            stop_reason = "freeze_complete"
            print(f"[round {round_num}] 전 변수 freeze → 종료.")
            break

    # 최종 결과
    ended = datetime.now()
    final_best_J = J_history[-1] if J_history else None
    full_final = {**neutral_values(), **frozen_vars, **current_best}

    final_payload = {
        "study_name":       args.study_name,
        "run_name":         run_name,
        "started":          started.isoformat(timespec="seconds"),
        "ended":            ended.isoformat(timespec="seconds"),
        "duration_sec":     (ended - started).total_seconds(),
        "stop_reason":      stop_reason,
        "thresholds": {
            "n_trial":      args.n_trial,
            "r_max":        args.r_max,
            "rho":          args.rho,
            "theta_J":      args.theta_J,
            "theta_freeze": args.theta_freeze,
        },
        "active_vars":      list(active_vars.keys()),
        "frozen_vars":      dict(frozen_vars),
        "current_best":     dict(current_best),
        "full_final":       full_final,
        "best_J":           final_best_J,
        "J_history":        J_history,
        "rounds":           rounds_summary,
        "inputs": {
            "baseline_osm":    str(baseline_osm),
            "baseline_params": str(baseline_params),
            "epw":             str(epw),
            "measured_elec":   str(measured_elec),
            "measured_gas":    str(measured_gas),
        },
        "outputs": {
            "run_root":    str(run_root),
            "study_db":    str(db_path),
            "summary_json": str(summaries_root / f"{run_name}_summary.json"),
        },
    }
    summary_path = summaries_root / f"{run_name}_summary.json"
    summary_path.write_text(
        json.dumps(final_payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"\n[run_phase1] DONE. stop_reason={stop_reason} best_J={final_best_J}")
    print(f"[run_phase1] Summary: {summary_path}")
    return final_payload


# ===========================================================================
# CLI
# ===========================================================================
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage 1 Optuna search (paper §3 iterative joint optimization)"
    )
    parser.add_argument("--study-name",      default=DEFAULT_STUDY_NAME)
    parser.add_argument("--baseline-osm",    default=str(DEFAULT_BASELINE_OSM))
    parser.add_argument("--baseline-params", default=str(DEFAULT_BASELINE_PARAMS))
    parser.add_argument("--epw",             default=str(DEFAULT_EPW))
    parser.add_argument("--measured-elec",   default=str(DEFAULT_MEASURED_ELEC))
    parser.add_argument("--measured-gas",    default=str(DEFAULT_MEASURED_GAS))
    parser.add_argument("--trials-root",     default=str(DEFAULT_TRIALS_ROOT))
    parser.add_argument("--studies-root",    default=str(DEFAULT_STUDIES_ROOT))
    parser.add_argument("--summaries-root",  default=str(DEFAULT_SUMMARIES_ROOT))
    parser.add_argument("--n-trial",         type=int,   default=DEFAULT_N_TRIAL)
    parser.add_argument("--r-max",           type=int,   default=DEFAULT_R_MAX)
    parser.add_argument("--rho",             type=float, default=DEFAULT_RHO)
    parser.add_argument("--theta-J",         type=float, default=DEFAULT_THETA_J)
    parser.add_argument("--theta-freeze",    type=float, default=DEFAULT_THETA_FREEZE)
    parser.add_argument(
        "--smoke", action="store_true",
        help="스모크: r_max=1, n_trial=2 강제 (파이프라인 검증용)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.smoke:
        args.r_max = 1
        args.n_trial = 2
        print("[smoke] r_max=1, n_trial=2")
    result = run_phase1(args)
    # 콘솔에 short 요약
    print("\n=== FINAL ===")
    print(json.dumps({
        "stop_reason": result["stop_reason"],
        "best_J":      result["best_J"],
        "frozen_vars": result["frozen_vars"],
        "current_best": result["current_best"],
        "summary":     result["outputs"]["summary_json"],
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
