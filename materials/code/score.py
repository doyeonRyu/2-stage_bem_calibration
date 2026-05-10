"""
File: score.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
시뮬레이션 결과와 실측 데이터를 비교해 Step 1 목적함수를 계산한다.

======================================================================
Description:
월별 전기 및 가스 사용량을 기준으로 CVRMSE, NMBE, annual error, ASHRAE Guideline 14
충족 여부, 그리고 Optuna 목적함수 J를 계산한다. Stage 1 search의 평가 기준을 담당하는 파일이다.

Input:
- 시뮬레이션 월별 결과 dict
- 실측 전기 CSV
- 실측 가스 CSV
- 가중치 dict

Output:
- 성능 지표 dict
- 목적함수 J
- residual 및 pass/fail 요약

======================================================================
Note:
기본 가중치는 ASHRAE Guideline 14 월별 기준을 정규화한 값이다.

======================================================================
Run:
python materials/code/score.py --help

"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]   # materials/
DEFAULT_MEASURED_ELEC = PROJECT_ROOT / "measured" / "electricity_monthly.csv"
DEFAULT_MEASURED_GAS  = PROJECT_ROOT / "measured" / "LNG_monthly.csv"

# ASHRAE Guideline 14 (monthly thresholds, %)
ASHRAE_G14_CVRMSE = 15.0
ASHRAE_G14_NMBE   = 5.0

# 기본 가중치: ASHRAE G14 정규화 (각 항이 threshold일 때 1.0)
DEFAULT_WEIGHTS: dict[str, float] = {
    "w_cvrmse_elec": 1.0 / ASHRAE_G14_CVRMSE,
    "w_cvrmse_gas":  1.0 / ASHRAE_G14_CVRMSE,
    "w_nmbe_elec":   1.0 / ASHRAE_G14_NMBE,
    "w_nmbe_gas":    1.0 / ASHRAE_G14_NMBE,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def compute_score(
    sim_results: dict[str, Any],
    measured_elec_path: Path | str = DEFAULT_MEASURED_ELEC,
    measured_gas_path:  Path | str = DEFAULT_MEASURED_GAS,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """월별 sim 결과 + 실측 → CVRMSE / NMBE / J + ASHRAE G14 pass.

    Args:
        sim_results:        simulation.extract_monthly_results() 반환 dict
                            (필수 키: electricity_kwh, gas_nm3 — 각각 {1..12: float})
        measured_elec_path: month,electricity_kwh CSV
        measured_gas_path:  month,gas_nm3 CSV
        weights:            4개 가중치 dict (None → ASHRAE G14 정규화)

    Returns:
        {
          "metrics":   {cvrmse_elec, cvrmse_gas, nmbe_elec, nmbe_gas,
                        annual_error_elec_pct, annual_error_gas_pct,
                        annual_abs_error_elec_pct, annual_abs_error_gas_pct},
          "weights":   dict,
          "J":         float,                 # 목적함수
          "ashrae_g14":{elec_cvrmse_pass, elec_nmbe_pass,
                        gas_cvrmse_pass, gas_nmbe_pass, all_pass},
          "annual":    {
              "elec": {"measured_total": ..., "simulated_total": ...},
              "gas":  {"measured_total": ..., "simulated_total": ...},
          },
          "residuals": {elec_kwh: {1..12: M-S}, gas_nm3: {1..12: M-S}},
          "monthly":   {                       # 비교 기록 (디버그/리포트용)
              "elec":  {1..12: {"measured": ..., "simulated": ...}},
              "gas":   {1..12: {"measured": ..., "simulated": ...}},
          },
          "warnings":  [str],
        }

    Note:
        sim/measured month 중 양쪽 모두 있는 달만 metric 계산에 포함.
        측정 단위와 sim 단위가 달라야 매칭됨 (elec=kWh, gas=Nm³).
    """
    weights = dict(DEFAULT_WEIGHTS) if weights is None else dict(weights)
    warnings: list[str] = []

    measured_elec = load_measured(measured_elec_path, "electricity_kwh")
    measured_gas  = load_measured(measured_gas_path,  "gas_nm3")

    sim_elec = _coerce_int_keys(sim_results.get("electricity_kwh") or {})
    sim_gas  = _coerce_int_keys(sim_results.get("gas_nm3")         or {})

    if not sim_elec:
        warnings.append("sim_results.electricity_kwh가 비어있음")
    if not sim_gas:
        warnings.append("sim_results.gas_nm3가 비어있음")

    cv_e = cvrmse(measured_elec, sim_elec)
    cv_g = cvrmse(measured_gas,  sim_gas)
    nb_e = nmbe(measured_elec,   sim_elec)
    nb_g = nmbe(measured_gas,    sim_gas)
    ae_e = annual_error_pct(measured_elec, sim_elec)
    ae_g = annual_error_pct(measured_gas,  sim_gas)

    J = (
        weights["w_cvrmse_elec"] * _safe(cv_e) +
        weights["w_cvrmse_gas"]  * _safe(cv_g) +
        weights["w_nmbe_elec"]   * _safe(abs(nb_e) if not math.isnan(nb_e) else nb_e) +
        weights["w_nmbe_gas"]    * _safe(abs(nb_g) if not math.isnan(nb_g) else nb_g)
    )

    ashrae = {
        "elec_cvrmse_pass": _le(cv_e, ASHRAE_G14_CVRMSE),
        "elec_nmbe_pass":   _le(abs(nb_e) if not math.isnan(nb_e) else nb_e, ASHRAE_G14_NMBE),
        "gas_cvrmse_pass":  _le(cv_g, ASHRAE_G14_CVRMSE),
        "gas_nmbe_pass":    _le(abs(nb_g) if not math.isnan(nb_g) else nb_g, ASHRAE_G14_NMBE),
    }
    ashrae["all_pass"] = all(ashrae.values())

    return {
        "metrics": {
            "cvrmse_elec": cv_e,
            "cvrmse_gas":  cv_g,
            "nmbe_elec":   nb_e,
            "nmbe_gas":    nb_g,
            "annual_error_elec_pct": ae_e,
            "annual_error_gas_pct":  ae_g,
            "annual_abs_error_elec_pct": abs(ae_e) if not math.isnan(ae_e) else ae_e,
            "annual_abs_error_gas_pct":  abs(ae_g) if not math.isnan(ae_g) else ae_g,
        },
        "weights":    weights,
        "J":          J,
        "ashrae_g14": ashrae,
        "annual": {
            "elec": _annual_totals(measured_elec, sim_elec),
            "gas":  _annual_totals(measured_gas,  sim_gas),
        },
        "residuals": {
            "elec_kwh": _residuals(measured_elec, sim_elec),
            "gas_nm3":  _residuals(measured_gas,  sim_gas),
        },
        "monthly": {
            "elec": _pair_monthly(measured_elec, sim_elec),
            "gas":  _pair_monthly(measured_gas,  sim_gas),
        },
        "warnings": warnings,
    }


def cvrmse(measured: dict[int, float], simulated: dict[int, float]) -> float:
    """ASHRAE G14: 100/m̄ · sqrt(Σ(M-S)² / n)  (%)
    매칭되는 월이 없거나 m̄=0이면 NaN.
    """
    months = sorted(set(measured) & set(simulated))
    if not months:
        return float("nan")
    M = [measured[m]  for m in months]
    S = [simulated[m] for m in months]
    n = len(M)
    m_bar = sum(M) / n
    if m_bar == 0:
        return float("nan")
    sse = sum((M[i] - S[i]) ** 2 for i in range(n))
    return 100.0 / m_bar * math.sqrt(sse / n)


def nmbe(measured: dict[int, float], simulated: dict[int, float]) -> float:
    """ASHRAE G14: 100 · Σ(M-S) / (n · m̄)  (%, signed)
    Positive = simulation 과소예측. 매칭 월 없거나 m̄=0이면 NaN.
    """
    months = sorted(set(measured) & set(simulated))
    if not months:
        return float("nan")
    M = [measured[m]  for m in months]
    S = [simulated[m] for m in months]
    n = len(M)
    m_bar = sum(M) / n
    if m_bar == 0:
        return float("nan")
    return 100.0 * sum(M[i] - S[i] for i in range(n)) / (n * m_bar)


def annual_error_pct(measured: dict[int, float], simulated: dict[int, float]) -> float:
    """연간 총량 기준 signed 오차율 (%).

    정의: 100 * (S_total - M_total) / M_total
    Positive = simulation 과대예측, Negative = simulation 과소예측.
    """
    months = sorted(set(measured) & set(simulated))
    if not months:
        return float("nan")
    measured_total = sum(measured[m] for m in months)
    simulated_total = sum(simulated[m] for m in months)
    if measured_total == 0:
        return float("nan")
    return 100.0 * (simulated_total - measured_total) / measured_total


def load_measured(csv_path: Path | str, value_col: str) -> dict[int, float]:
    """월별 실측 CSV 로드. CSV format: 'month,<value_col>' 헤더."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Measured CSV not found: {csv_path}")
    out: dict[int, float] = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "month" not in reader.fieldnames or value_col not in reader.fieldnames:
            raise ValueError(
                f"CSV columns invalid: {reader.fieldnames} "
                f"(필요: 'month', '{value_col}')"
            )
        for row in reader:
            m = int(row["month"])
            v = float(row[value_col])
            out[m] = v
    return out


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _coerce_int_keys(d: dict) -> dict[int, float]:
    """JSON round-trip으로 str이 된 month 키를 int로 강제."""
    return {int(k): float(v) for k, v in d.items()}


def _safe(x: float) -> float:
    """NaN을 J 계산에서 0으로 (warning은 별도 기록)."""
    return 0.0 if (x is None or math.isnan(x)) else x


def _le(x: float, threshold: float) -> bool:
    """NaN은 fail."""
    if x is None or math.isnan(x):
        return False
    return x <= threshold


def _residuals(measured: dict[int, float], simulated: dict[int, float]) -> dict[int, float]:
    """M - S 잔차 (양수=sim 과소예측)."""
    months = sorted(set(measured) & set(simulated))
    return {m: measured[m] - simulated[m] for m in months}


def _annual_totals(
    measured: dict[int, float], simulated: dict[int, float]
) -> dict[str, float | None]:
    months = sorted(set(measured) & set(simulated))
    if not months:
        return {"measured_total": None, "simulated_total": None}
    return {
        "measured_total": sum(measured[m] for m in months),
        "simulated_total": sum(simulated[m] for m in months),
    }


def _pair_monthly(
    measured: dict[int, float], simulated: dict[int, float]
) -> dict[int, dict[str, float]]:
    months = sorted(set(measured) | set(simulated))
    return {
        m: {
            "measured":  measured.get(m),
            "simulated": simulated.get(m),
        }
        for m in months
    }


# ===========================================================================
# CLI
# ===========================================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Score E+ sim 결과 vs 실측 (CVRMSE / NMBE / J)"
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--sim-json",
        help="simulation.py 출력 JSON (전체 payload 또는 results dict)",
    )
    src.add_argument(
        "--simulation-dir",
        help=(
            "OSW output dir 또는 eplusout.sql 직접 경로. "
            "디렉터리면 <dir>/run/eplusout.sql, 파일이면 그대로 사용."
        ),
    )
    parser.add_argument("--measured-elec", default=str(DEFAULT_MEASURED_ELEC))
    parser.add_argument("--measured-gas",  default=str(DEFAULT_MEASURED_GAS))
    parser.add_argument(
        "--weights-json",
        help="가중치 dict JSON (키: w_cvrmse_elec, w_cvrmse_gas, w_nmbe_elec, w_nmbe_gas)",
    )
    parser.add_argument("--out", help="결과 score JSON 저장 경로 (옵션)")
    args = parser.parse_args()

    if args.sim_json:
        with open(args.sim_json, encoding="utf-8") as f:
            payload = json.load(f)
        sim_results = payload.get("results") or payload
        if sim_results is None:
            parser.error(f"sim-json의 'results' 키가 None: 시뮬 실패한 결과로 보입니다")
    else:
        from simulation import extract_monthly_results
        p = Path(args.simulation_dir)
        # SQL 파일 직접 / OSW 출력 dir 자동 감지
        if p.is_file() and p.suffix.lower() == ".sql":
            sql = p
        elif (p / "run" / "eplusout.sql").exists():
            sql = p / "run" / "eplusout.sql"
        elif (p / "eplusout.sql").exists():
            sql = p / "eplusout.sql"
        else:
            parser.error(
                f"--simulation-dir 경로에서 eplusout.sql을 찾을 수 없음: {p}\n"
                "  허용 형태:\n"
                "    1) /path/to/<study>/<trial>/run/eplusout.sql 직접\n"
                "    2) /path/to/<study>/<trial>/  (run/eplusout.sql 자동 부착)\n"
                "    3) /path/to/run/             (eplusout.sql 자동 부착)"
            )
        sim_results = extract_monthly_results(sql)

    weights = None
    if args.weights_json:
        with open(args.weights_json, encoding="utf-8") as f:
            weights = json.load(f)

    score = compute_score(
        sim_results,
        measured_elec_path=args.measured_elec,
        measured_gas_path=args.measured_gas,
        weights=weights,
    )

    text = json.dumps(score, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)
