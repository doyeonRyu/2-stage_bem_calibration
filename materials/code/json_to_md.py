"""
File: json_to_md.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
평가 JSON 결과를 Markdown 보고서 형식으로 변환한다.

======================================================================
Description:
평가 스크립트가 생성한 JSON 파일에서 핵심 지표와 월별 비교 결과를 읽어 사람이 바로 검토할 수 있는
Markdown 문서로 정리한다. 결과 공유와 기록용 보조 스크립트다.

Input:
- 평가 결과 JSON 파일

Output:
- Markdown 보고서 파일
- 콘솔 변환 로그

======================================================================
Note:
계산 로직은 포함하지 않고, 이미 생성된 결과를 문서화 형태로 재구성한다.

======================================================================
Run:
python materials/code/json_to_md.py --help

"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


_WIN_USER = next((n for n in ("ryudo", "USER") if Path(f"/mnt/c/Users/{n}").exists()), "ryudo")


def resolve_path(path_str: str) -> Path:
    if len(path_str) >= 3 and path_str[1:3] == ":\\":
        drive = path_str[0].lower()
        suffix = path_str[3:].replace("\\", "/")
        return Path(f"/mnt/{drive}/{suffix}")
    return Path(path_str.replace("\\", "/"))


DEFAULT_OSM_DIR = resolve_path(
    rf"C:\Users\{_WIN_USER}\OneDrive - gachon.ac.kr\2-stage_osm_calibration-osm\osm"
)


def resolve_input_path(input_arg: str) -> Path:
    candidate = resolve_path(input_arg)
    if candidate.exists():
        return candidate

    raw = input_arg.replace("\\", "/")
    if "/" not in raw:
        default_candidate = DEFAULT_OSM_DIR / raw
        if default_candidate.exists():
            return default_candidate

    if raw.endswith(".json") and "/" not in raw:
        default_candidate = DEFAULT_OSM_DIR / raw.removesuffix(".json")
        if default_candidate.exists():
            return default_candidate / "evaluation.json"

    return candidate


def load_payload(input_path: Path) -> tuple[dict[str, Any], Path]:
    if input_path.is_dir():
        json_path = input_path / "evaluation.json"
    else:
        json_path = input_path
    if not json_path.exists():
        raise FileNotFoundError(f"evaluation.json을 찾을 수 없습니다: {json_path}")
    with json_path.open(encoding="utf-8") as f:
        return json.load(f), json_path


def fmt_num(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    return f"{float(value):,.{digits}f}"


def fmt_pct(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    return f"{float(value):.{digits}f}%"


def build_metrics_table(score: dict[str, Any]) -> list[str]:
    metrics = score["metrics"]
    return [
        "| 항목 | 전력 | 가스 |",
        "|---|---:|---:|",
        f"| CVRMSE | {fmt_pct(metrics.get('cvrmse_elec'))} | {fmt_pct(metrics.get('cvrmse_gas'))} |",
        f"| NMBE | {fmt_pct(metrics.get('nmbe_elec'))} | {fmt_pct(metrics.get('nmbe_gas'))} |",
        f"| 연오차 | {fmt_pct(metrics.get('annual_error_elec_pct'))} | {fmt_pct(metrics.get('annual_error_gas_pct'))} |",
        f"| 절대 연오차 | {fmt_pct(metrics.get('annual_abs_error_elec_pct'))} | {fmt_pct(metrics.get('annual_abs_error_gas_pct'))} |",
    ]


def build_annual_table(score: dict[str, Any]) -> list[str]:
    annual = score.get("annual", {})
    elec = annual.get("elec", {})
    gas = annual.get("gas", {})
    return [
        "| 항목 | 전력 (kWh) | 가스 (Nm3) |",
        "|---|---:|---:|",
        f"| 실측 연간합 | {fmt_num(elec.get('measured_total'))} | {fmt_num(gas.get('measured_total'))} |",
        f"| 시뮬 연간합 | {fmt_num(elec.get('simulated_total'))} | {fmt_num(gas.get('simulated_total'))} |",
    ]


def build_monthly_table(monthly: dict[str, Any], residuals: dict[str, Any], title: str, unit: str) -> list[str]:
    lines = [
        f"## {title}",
        "",
        f"| 월 | 실측 ({unit}) | 시뮬 ({unit}) | 잔차 M-S ({unit}) |",
        "|---:|---:|---:|---:|",
    ]
    for month in range(1, 13):
        item = monthly.get(str(month)) or monthly.get(month) or {}
        residual = residuals.get(str(month))
        if residual is None:
            residual = residuals.get(month)
        lines.append(
            f"| {month} | {fmt_num(item.get('measured'))} | {fmt_num(item.get('simulated'))} | {fmt_num(residual)} |"
        )
    return lines


def build_md(payload: dict[str, Any]) -> str:
    inputs = payload.get("inputs", {})
    score = payload.get("score", {})
    summary = payload.get("summary", {})
    monthly = score.get("monthly", {})
    residuals = score.get("residuals", {})
    warnings = summary.get("warnings", [])

    lines = [
        "# Evaluation Report",
        "",
        f"- OSM: `{inputs.get('osm', '-')}`",
        f"- SQL: `{payload.get('simulation', {}).get('sql_path', '-')}`",
        f"- J: {fmt_num(summary.get('J'))}",
        "",
        "## Metrics",
        "",
        *build_metrics_table(score),
        "",
        "## Annual Totals",
        "",
        *build_annual_table(score),
        "",
        *build_monthly_table(monthly.get("elec", {}), residuals.get("elec_kwh", {}), "월별 전력", "kWh"),
        "",
        *build_monthly_table(monthly.get("gas", {}), residuals.get("gas_nm3", {}), "월별 가스", "Nm3"),
    ]

    if warnings:
        lines.extend([
            "",
            "## Warnings",
            "",
        ])
        for warning in warnings:
            lines.append(f"- {warning}")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="evaluation.json을 Markdown 리포트로 변환"
    )
    parser.add_argument(
        "input",
        help="evaluation.json 경로 또는 evaluation.json이 있는 폴더",
    )
    parser.add_argument(
        "--out",
        help="출력 Markdown 경로. 기본값: <input_dir>/evaluation.md",
    )
    args = parser.parse_args()

    input_path = resolve_input_path(args.input)
    payload, json_path = load_payload(input_path)

    out_path = resolve_path(args.out) if args.out else json_path.with_suffix(".md")
    out_path.write_text(build_md(payload), encoding="utf-8")

    print(f"saved_md: {out_path}")


if __name__ == "__main__":
    main()
