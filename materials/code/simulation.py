"""
File: simulation.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
OpenStudio CLI 기반으로 OSM 시뮬레이션을 실행하고 월별 에너지 결과를 추출한다.

======================================================================
Description:
trial OSM과 EPW를 입력으로 EnergyPlus 시뮬레이션을 수행하고, 결과 SQL에서 월별 전력 및 가스
사용량을 읽어 후속 score 계산에 전달한다. Stage 1 trial 평가와 단일 OSM 평가에서 공통으로
사용되는 실행 계층이다.

Input:
- OSM 파일
- EPW 파일
- 출력 디렉터리
- OpenStudio CLI 설정값

Output:
- 시뮬레이션 실행 결과
- 월별 전력/가스 결과 dict
- 실행 로그 및 상태 요약

======================================================================
Note:
무거운 trial 산출물은 현재 환경 제약 때문에 기본적으로 C 드라이브 비-OneDrive 경로에 저장한다.

======================================================================
Run:
python materials/code/simulation.py --help

"""

from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path
from typing import Any

import openstudio


def _resolve_path(path_str: str) -> Path:
    """Normalize Windows-style paths when running from WSL/Linux."""
    if len(path_str) >= 3 and path_str[1:3] == ":\\":
        drive = path_str[0].lower()
        suffix = path_str[3:].replace("\\", "/")
        return Path(f"/mnt/{drive}/{suffix}")
    return Path(path_str.replace("\\", "/"))


def _to_openstudio_path(path_like: Path | str) -> str:
    """Convert /mnt/<drive>/... paths back to Windows form for openstudio.exe."""
    p = Path(path_like).resolve()
    parts = p.parts
    if len(parts) >= 4 and parts[1] == "mnt" and len(parts[2]) == 1:
        drive = parts[2].upper()
        rest = "\\".join(parts[3:])
        return f"{drive}:\\{rest}"
    return str(p)


# ---------------------------------------------------------------------------
# Defaults (Windows 환경 기준)
# ---------------------------------------------------------------------------
DEFAULT_OUTPUT_ROOT = _resolve_path(r"C:\Users\ryudo\optuna_trials")
# Note: openstudio Python이 E:에 write 못함 → trial 출력은 C: 비-OneDrive 경로.
DEFAULT_EPW = _resolve_path(
    r"C:\Users\ryudo\OneDrive - gachon.ac.kr\2-stage_osm_calibration-osm\KOR_CB_Jeonju.471460_TMYx.2011-2025.epw"
)
DEFAULT_OPENSTUDIO_BIN = "openstudio"  # PATH 우선, 없으면 _resolve_openstudio_cli()가 탐지

# LNG 표준 발열량 (한국가스공사 기준): 10.55 kWh/Nm³
LNG_KWH_PER_NM3 = 10.55

# Monthly meter (E+ 9.0+: NaturalGas, 8.x: Gas)
ELEC_METER = "Electricity:Facility"
GAS_METER_PRIMARY = "NaturalGas:Facility"
GAS_METER_LEGACY = "Gas:Facility"

# OpenStudio CLI subprocess timeout (s)
DEFAULT_TIMEOUT_SEC = 1800


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def run_simulation(
    osm_path: Path | str,
    epw_path: Path | str = DEFAULT_EPW,
    output_dir: Path | str | None = None,
    openstudio_bin: str = DEFAULT_OPENSTUDIO_BIN,
    ensure_meters: bool = True,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> dict[str, Any]:
    """OpenStudio CLI(`openstudio run -w workflow.osw`)로 OSM 시뮬레이션 실행.

    Args:
        osm_path:       trial OSM (apply_calibrated_vars.write_applied_to_osm 산출)
        epw_path:       weather file (EPW)
        output_dir:     출력 디렉터리. None이면 DEFAULT_OUTPUT_ROOT/<osm_stem>/
        openstudio_bin: openstudio CLI binary 이름 또는 절대 경로
        ensure_meters:  OSM에 월별 OutputMeter가 없으면 자동 추가 (기본 True)
        timeout_sec:    subprocess timeout

    Returns:
        {
          "osm_path": str, "epw_path": str,
          "osw_path": str, "run_dir": str, "sql_path": str,
          "status": "success" | "failed" | "timeout",
          "returncode": int,
          "stdout_tail": str, "stderr_tail": str
        }
    """
    osm_path = Path(osm_path).resolve()
    epw_path = Path(epw_path).resolve()
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_ROOT / osm_path.stem
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not osm_path.exists():
        raise FileNotFoundError(f"OSM not found: {osm_path}")
    if not epw_path.exists():
        raise FileNotFoundError(f"EPW not found: {epw_path}")

    if ensure_meters:
        _ensure_monthly_meters(osm_path)

    resolved_bin = _resolve_openstudio_cli(openstudio_bin)

    osw_path = output_dir / "workflow.osw"
    run_dir = output_dir / "run"

    osw = {
        "seed_file":     _to_openstudio_path(osm_path),
        "weather_file":  _to_openstudio_path(epw_path),
        "measure_paths": [],
        "steps":         [],
        "run_directory": _to_openstudio_path(run_dir),
    }
    osw_path.write_text(json.dumps(osw, indent=2), encoding="utf-8")

    cmd = [resolved_bin, "run", "-w", _to_openstudio_path(osw_path)]
    status = "failed"
    rc = -1
    stdout = ""
    stderr = ""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_sec
        )
        rc = result.returncode
        stdout = result.stdout or ""
        stderr = result.stderr or ""
    except subprocess.TimeoutExpired as e:
        status = "timeout"
        stdout = (e.stdout or "") if isinstance(e.stdout, str) else ""
        stderr = (e.stderr or "") if isinstance(e.stderr, str) else ""
        stderr += f"\n[TIMEOUT] subprocess exceeded {timeout_sec}s"

    sql_path = run_dir / "eplusout.sql"
    if status != "timeout":
        status = "success" if (rc == 0 and sql_path.exists()) else "failed"

    return {
        "osm_path":       str(osm_path),
        "epw_path":       str(epw_path),
        "osw_path":       str(osw_path),
        "run_dir":        str(run_dir),
        "sql_path":       str(sql_path),
        "openstudio_bin": resolved_bin,
        "status":         status,
        "returncode":     rc,
        "stdout_tail":    stdout[-1500:],
        "stderr_tail":    stderr[-1500:],
    }


def extract_monthly_results(sql_path: Path | str) -> dict[str, Any]:
    """eplusout.sql에서 월별 전력/가스 사용량 추출.

    Returns:
        {
          "electricity_kwh":  {1..12: float},
          "gas_kwh":          {1..12: float},
          "gas_nm3":          {1..12: float},   # LNG 10.55 kWh/Nm³ 환산
          "annual": {
              "electricity_kwh_total": float,
              "gas_kwh_total":         float,
              "gas_nm3_total":         float,
          },
          "warnings": [str],
        }

    Note: 측정 데이터는 monthly이므로 이 12개 값과 직접 비교한다.
          가스 단위 변환은 score.py가 사용. measured CSV가 Nm³이면 gas_nm3 사용.
    """
    sql_path = Path(sql_path)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL not found: {sql_path}")

    elec_J = _query_monthly_meter(sql_path, ELEC_METER)
    gas_J = _query_monthly_meter(sql_path, GAS_METER_PRIMARY)
    if not gas_J:
        gas_J = _query_monthly_meter(sql_path, GAS_METER_LEGACY)

    warnings: list[str] = []
    if not elec_J:
        warnings.append(f"No monthly meter '{ELEC_METER}' in SQL")
    if not gas_J:
        warnings.append(
            f"No monthly meter '{GAS_METER_PRIMARY}' or '{GAS_METER_LEGACY}' in SQL"
        )

    J_TO_KWH = 1.0 / 3.6e6
    elec_kwh = {m: v * J_TO_KWH for m, v in elec_J.items()}
    gas_kwh = {m: v * J_TO_KWH for m, v in gas_J.items()}
    gas_nm3 = {m: v / LNG_KWH_PER_NM3 for m, v in gas_kwh.items()}

    return {
        "electricity_kwh": elec_kwh,
        "gas_kwh":         gas_kwh,
        "gas_nm3":         gas_nm3,
        "annual": {
            "electricity_kwh_total": sum(elec_kwh.values()),
            "gas_kwh_total":         sum(gas_kwh.values()),
            "gas_nm3_total":         sum(gas_nm3.values()),
        },
        "warnings": warnings,
    }


def simulate_and_extract(
    osm_path: Path | str,
    epw_path: Path | str = DEFAULT_EPW,
    output_dir: Path | str | None = None,
    **run_kwargs,
) -> dict[str, Any]:
    """run + extract 한 번에 실행. score.py에서 호출용."""
    sim = run_simulation(osm_path, epw_path, output_dir, **run_kwargs)
    if sim["status"] != "success":
        return {"simulation": sim, "results": None}
    results = extract_monthly_results(sim["sql_path"])
    return {"simulation": sim, "results": results}


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
def _resolve_openstudio_cli(openstudio_bin: str) -> str:
    """openstudio CLI 실행파일 경로 해결.

    탐지 순서:
      1. openstudio_bin이 절대 경로 + 존재 → 그대로 사용
      2. shutil.which (PATH)
      3. C:\\openstudioapplication-*\\bin\\openstudio.exe (글로브)
      4. C:\\openstudio-*\\bin\\openstudio.exe (글로브, SDK 단독 설치 케이스)

    Raises:
        FileNotFoundError: 어느 경로에서도 찾지 못함.
    """
    import shutil
    import glob

    p = _resolve_path(openstudio_bin)
    if p.is_absolute() and p.exists():
        return str(p)

    found = shutil.which(openstudio_bin)
    if found:
        return found

    candidates: list[str] = []
    for pattern in (
        r"C:\openstudioapplication-*\bin\openstudio.exe",
        r"C:\openstudio-*\bin\openstudio.exe",
        r"C:\Program Files\openstudioapplication-*\bin\openstudio.exe",
        r"C:\Program Files\OpenStudioApplication-*\bin\openstudio.exe",
        r"/mnt/c/openstudioapplication-*/bin/openstudio.exe",
        r"/mnt/c/openstudio-*/bin/openstudio.exe",
        r"/mnt/c/Program Files/openstudioapplication-*/bin/openstudio.exe",
        r"/mnt/c/Program Files/OpenStudioApplication-*/bin/openstudio.exe",
        r"/mnt/c/Program Files/NREL/OpenStudio CLI For Revit */bin/openstudio.exe",
    ):
        candidates.extend(glob.glob(pattern))
    if candidates:
        candidates.sort(reverse=True)  # 최신 버전 우선
        return candidates[0]

    raise FileNotFoundError(
        f"openstudio CLI를 찾을 수 없습니다. (입력값: '{openstudio_bin}')\n"
        "다음 중 하나로 해결하세요:\n"
        "  - --openstudio-bin 으로 절대 경로 지정\n"
        "    (예: C:\\openstudioapplication-1.11.0\\bin\\openstudio.exe)\n"
        "  - openstudio.exe가 있는 dir을 PATH에 추가\n"
        "  - simulation.py의 _resolve_openstudio_cli 글로브 패턴에 설치 경로 추가"
    )


def _ensure_monthly_meters(osm_path: Path) -> None:
    """OSM에 월별 OutputMeter (Elec / NaturalGas)가 없으면 추가 후 저장.

    이미 존재하면 no-op. write_applied_to_osm()이 baseline OSM의 OutputMeter를
    보존하므로 baseline에 한 번만 추가되어 있어도 trial OSM마다 자동 유지됨.
    """
    loaded = openstudio.osversion.VersionTranslator().loadModel(
        openstudio.path(str(osm_path))
    )
    if not loaded.is_initialized():
        raise RuntimeError(f"Cannot load OSM: {osm_path}")
    model = loaded.get()

    existing: set[tuple[str, str]] = set()
    for om in model.getOutputMeters():
        existing.add((om.name(), om.reportingFrequency()))

    needed = [
        (ELEC_METER,         "Monthly"),
        (GAS_METER_PRIMARY,  "Monthly"),
    ]
    changed = False
    for name, freq in needed:
        if (name, freq) not in existing:
            om = openstudio.model.OutputMeter(model)
            om.setName(name)
            om.setReportingFrequency(freq)
            changed = True

    if changed:
        model.save(openstudio.path(str(osm_path)), True)


def _query_monthly_meter(sql_path: Path, meter_name: str) -> dict[int, float]:
    """eplusout.sql ReportMeterData 테이블에서 월별 미터 값 조회 (J 단위).

    우선 Monthly meter를 직접 읽고, 없으면 Daily meter를 RunPeriod 기준으로
    월별 합산해서 반환한다.

    Returns: {month_int: value_J} (없으면 빈 dict).
    """
    conn = sqlite3.connect(str(sql_path))
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT t.Month, r.VariableValue
            FROM ReportMeterData r
            JOIN ReportMeterDataDictionary d
                ON r.ReportMeterDataDictionaryIndex = d.ReportMeterDataDictionaryIndex
            JOIN Time t
                ON r.TimeIndex = t.TimeIndex
            JOIN EnvironmentPeriods e
                ON t.EnvironmentPeriodIndex = e.EnvironmentPeriodIndex
            WHERE d.VariableName = ?
              AND d.ReportingFrequency = 'Monthly'
              AND t.Month BETWEEN 1 AND 12
              AND t.WarmupFlag = 0
              AND e.EnvironmentType = 3
            ORDER BY t.Month
            """,
            (meter_name,),
        )
        rows = cur.fetchall()
        if rows:
            return {int(m): float(v) for m, v in rows}

        cur.execute(
            """
            SELECT t.Month, SUM(r.VariableValue)
            FROM ReportMeterData r
            JOIN ReportMeterDataDictionary d
                ON r.ReportMeterDataDictionaryIndex = d.ReportMeterDataDictionaryIndex
            JOIN Time t
                ON r.TimeIndex = t.TimeIndex
            JOIN EnvironmentPeriods e
                ON t.EnvironmentPeriodIndex = e.EnvironmentPeriodIndex
            WHERE d.VariableName = ?
              AND d.ReportingFrequency = 'Daily'
              AND t.Month BETWEEN 1 AND 12
              AND t.WarmupFlag = 0
              AND e.EnvironmentType = 3
            GROUP BY t.Month
            ORDER BY t.Month
            """,
            (meter_name,),
        )
        rows = cur.fetchall()
    except sqlite3.Error:
        rows = []
    finally:
        conn.close()
    return {int(m): float(v) for m, v in rows}


# ===========================================================================
# CLI
# ===========================================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run E+ simulation via OpenStudio CLI (eplus venv)"
    )
    parser.add_argument("--osm", required=True, help="trial OSM path")
    parser.add_argument("--epw", default=str(DEFAULT_EPW), help="EPW weather file")
    parser.add_argument(
        "--out", default=None,
        help="output dir (default: DEFAULT_OUTPUT_ROOT/<osm_stem>)",
    )
    parser.add_argument(
        "--openstudio-bin", default=DEFAULT_OPENSTUDIO_BIN,
        help="openstudio CLI binary (default: 'openstudio' on PATH)",
    )
    parser.add_argument(
        "--no-ensure-meters", action="store_true",
        help="OSM에 월별 OutputMeter 자동 추가 비활성화",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SEC)
    parser.add_argument(
        "--results-only", action="store_true",
        help="기존 run/eplusout.sql만 추출 (시뮬 재실행 X)",
    )
    args = parser.parse_args()

    if args.results_only:
        if args.out is None:
            out_dir = DEFAULT_OUTPUT_ROOT / Path(args.osm).stem
        else:
            out_dir = Path(args.out)
        sql = out_dir / "run" / "eplusout.sql"
        payload = {
            "simulation": {"sql_path": str(sql), "status": "skipped"},
            "results": extract_monthly_results(sql),
        }
    else:
        payload = simulate_and_extract(
            osm_path=args.osm,
            epw_path=args.epw,
            output_dir=args.out,
            openstudio_bin=args.openstudio_bin,
            ensure_meters=not args.no_ensure_meters,
            timeout_sec=args.timeout,
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
