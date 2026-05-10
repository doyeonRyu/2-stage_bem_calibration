"""
File: apply_calibrated_vars.py

> Date: 2026-05-10
> Author: 유도연

======================================================================
Purpose:
Optuna calibration 변수를 baseline 파라미터와 실제 OSM 모델에 반영한다.

======================================================================
Description:
baseline params dict에 multiplier, offset, shift 값을 적용해 계산 결과를 만들고,
필요할 경우 OpenStudio setter를 사용해 실제 trial OSM 파일로 저장한다. Stage 1 trial 생성의
핵심 적용 계층이다.

Input:
- baseline params dict
- Optuna 변수값 dict
- baseline OSM 경로
- 출력 OSM 경로

Output:
- 적용된 파라미터 dict
- trial OSM 파일
- 적용 요약 정보

======================================================================
Note:
원본 baseline dict는 직접 수정하지 않고 deep copy 기반으로 처리한다.

======================================================================
Run:
python materials/code/apply_calibrated_vars.py --help

"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from optuna_search_space import OPTUNA_SEARCH_SPACE, neutral_values

# openstudio는 OSM 쓰기 모드에서만 필요 — dict-only 사용시엔 SDK 없는 환경에서도 import 가능하게 lazy
try:
    import openstudio  # type: ignore
    from osm_calibration_params import _load_model, _name_of, _opt_get, _opt_value
    _OS_AVAILABLE = True
except ImportError:
    openstudio = None  # type: ignore
    _OS_AVAILABLE = False


def apply_optuna_vars(
    baseline: dict[str, Any],
    optuna_vars: dict[str, float | int] | None = None,
) -> dict[str, Any]:
    """baseline['candidates']의 22개 변수 target에 적용값을 채운 dict 반환.

    Args:
        baseline:    extract_baseline_params() 결과 (전체 dict).
        optuna_vars: Optuna trial이 sample한 변수 dict. None이면 neutral(no-op).

    Returns:
        baseline의 deep copy 후 candidates 섹션이 적용된 dict.
        metadata.applied_vars에 어떤 값이 적용됐는지 기록.
    """
    applied = copy.deepcopy(baseline)
    vars_in = {**neutral_values(), **(optuna_vars or {})}

    _apply_candidate_variables(applied, vars_in)

    applied.setdefault("metadata", {})["applied_vars"] = vars_in
    return applied


def _apply_candidate_variables(applied: dict, vars_in: dict[str, float | int]) -> None:
    candidates = applied.get("candidates", {})

    for name, entry in candidates.items():
        targets = entry.get("targets", [])
        if name in (
            "equipment_multiplier",
            "lighting_multiplier",
            "occupancy_density_multiplier",
            "infiltration_multiplier",
            "wall_u_multiplier",
            "roof_u_multiplier",
            "window_u_multiplier",
            "window_shgc_multiplier",
            "floor_u_multiplier",
            "oa_flow_multiplier",
            "fan_power_multiplier",
            "boiler_efficiency_multiplier",
            "chiller_cop_multiplier",
            "dhw_use_multiplier",
            "thermal_mass_multiplier",
        ):
            _apply_multiplier_targets(targets, float(vars_in[name]))
        elif name in (
            "occupancy_schedule_multiplier",
            "lighting_schedule_multiplier",
            "equipment_schedule_multiplier",
        ):
            _apply_schedule_targets(targets, float(vars_in[name]), cap_at_one=True)
        elif name == "hvac_availability_shift":
            _apply_schedule_shift_targets(targets, int(vars_in[name]))
        elif name == "heating_setpoint_offset":
            _apply_thermostat_targets(targets, float(vars_in[name]), 0.0, 0.0)
        elif name == "cooling_setpoint_offset":
            _apply_thermostat_targets(targets, 0.0, float(vars_in[name]), 0.0)
        elif name == "setback_delta_offset":
            _apply_thermostat_targets(targets, 0.0, 0.0, float(vars_in[name]))


def _apply_multiplier_targets(targets: list[dict], multiplier: float) -> None:
    for target in targets:
        baseline_value = target.get("baseline_value")
        if baseline_value is not None:
            target["applied_value"] = baseline_value * multiplier
        for key in (
            "design_flow_rate", "flow_per_area", "flow_per_ext_area", "ach",
            "flow_per_person", "flow_per_zone", "peak_flow_m3_s",
            "efficiency", "cop", "pressure_rise", "surface_area_m2",
            "area_per_floor", "surface_thermal_capacity_kJ_K",
        ):
            if target.get(key) is not None:
                target[f"{key}_applied"] = target[key] * multiplier
        target["multiplier"] = multiplier


def _apply_schedule_targets(targets: list[dict], multiplier: float, cap_at_one: bool) -> None:
    for target in targets:
        summary = target.get("summary")
        if isinstance(summary, dict):
            _scale_schedule_summary(summary, multiplier, cap_at_one=cap_at_one)
        target["multiplier"] = multiplier


def _apply_schedule_shift_targets(targets: list[dict], shift_h: int) -> None:
    for target in targets:
        summary = target.get("summary")
        if isinstance(summary, dict):
            _shift_schedule_times(summary, shift_h)
        target["shift_h"] = shift_h


def _apply_thermostat_targets(targets: list[dict], h_off: float, c_off: float, sb: float) -> None:
    for target in targets:
        h_occ = target.get("htg_occupied")
        c_occ = target.get("clg_occupied")
        if (h_occ is not None and c_occ is not None
                and (c_occ - h_occ) < DEADBAND_PROTECTION_MIN):
            target["adjusted"] = False
            continue
        if h_occ is not None:
            target["htg_occupied_applied"] = h_occ + h_off
        if target.get("htg_setback") is not None:
            target["htg_setback_applied"] = target["htg_setback"] + h_off - sb
        if c_occ is not None:
            target["clg_occupied_applied"] = c_occ + c_off
        if target.get("clg_setback") is not None:
            target["clg_setback_applied"] = target["clg_setback"] + c_off + sb
        target["adjusted"] = True


# ---------------------------------------------------------------------------
# Per-category applicators
# ---------------------------------------------------------------------------
def _apply_equipment(applied: dict, v: dict) -> None:
    m = v["equipment_multiplier"]
    eq = applied["candidates"]["equipment"]

    for info in eq["by_space_type"].values():
        info["w_m2_total_applied"] = (info.get("w_m2_total") or 0.0) * m
        info["multiplier"] = m
        for obj in info.get("objects", []):
            obj["w_m2_applied"] = (obj.get("w_m2") or 0.0) * m

    for zinfo in eq["by_zone"].values():
        zinfo["w_m2_applied"] = (zinfo.get("w_m2") or 0.0) * m
        zinfo["multiplier"] = m


def _apply_lighting(applied: dict, v: dict) -> None:
    m = v["lighting_multiplier"]
    lt = applied["candidates"]["lighting"]
    for info in lt["by_space_type"].values():
        info["w_m2_total_applied"] = (info.get("w_m2_total") or 0.0) * m
        info["multiplier"] = m
        for obj in info.get("objects", []):
            obj["w_m2_applied"] = (obj.get("w_m2") or 0.0) * m
    for zinfo in lt["by_zone"].values():
        zinfo["w_m2_applied"] = (zinfo.get("w_m2") or 0.0) * m
        zinfo["multiplier"] = m


def _apply_occupancy(applied: dict, v: dict) -> None:
    density_m  = v["occupancy_density_multiplier"]
    schedule_m = v["occupancy_schedule_multiplier"]
    occ = applied["candidates"]["occupancy"]

    for info in occ["by_space_type"].values():
        info["people_per_m2_applied"] = (info.get("people_per_m2") or 0.0) * density_m
        info["multiplier"] = density_m
        for obj in info.get("objects", []):
            obj["people_per_m2_applied"] = (obj.get("people_per_m2") or 0.0) * density_m

    for sch_name, summary in occ.get("schedules", {}).items():
        _scale_schedule_summary(summary, schedule_m, cap_at_one=True)


# 베이스라인 deadband가 이 값 미만인 zone은 thermostat offset 적용에서 제외.
# 운영 사양상 setpoint가 비-candidates인 zone(cleanroom, precision room, 항온항습실 등)
# 보호 — offset 적용 시 heating > cooling crossing으로 E+ Fatal 유발. paper §3.5
# reality hard constraint를 Stage 1에서 사전 적용 (building-agnostic 임계값 기반).
#
# KETI 케이스에서 보호되는 zone (참고용; 코드는 deadband로 자동 검출):
#   - TZ-FAB-CR    (cleanroom):       baseline deadband = 1.0
#   - TZ-FAB-PREC  (precision room):  baseline deadband = 0.0
DEADBAND_PROTECTION_MIN = 1.5  # °C


def _apply_thermostat(applied: dict, v: dict) -> None:
    """
    heating_setpoint_offset / cooling_setpoint_offset: occupied + setback 둘 다 평행이동.
    setback_delta_offset: occupied는 고정, setback만 추가 이동.
        - 양수면 setback이 더 멀어짐 (난방 setback ↓, 냉방 setback ↑)

    Cleanroom-class 보호: baseline deadband(clg_occupied - htg_occupied) <
    DEADBAND_PROTECTION_MIN인 zone은 offset 적용 X (baseline 값 그대로).
    skipped_zones에 기록 → reality 검토 추적용.
    """
    h_off = v["heating_setpoint_offset"]
    c_off = v["cooling_setpoint_offset"]
    sb    = v["setback_delta_offset"]
    th = applied["candidates"]["thermostat"]
    skipped_zones: list[str] = []

    for zname, z in th["by_zone"].items():
        h_occ = z.get("htg_occupied")
        c_occ = z.get("clg_occupied")
        # cleanroom-class 보호
        if (h_occ is not None and c_occ is not None
                and (c_occ - h_occ) < DEADBAND_PROTECTION_MIN):
            z["htg_occupied_applied"] = h_occ
            z["clg_occupied_applied"] = c_occ
            if z.get("htg_setback") is not None:
                z["htg_setback_applied"] = z["htg_setback"]
            if z.get("clg_setback") is not None:
                z["clg_setback_applied"] = z["clg_setback"]
            z["adjusted"] = False
            z["skip_reason"] = f"baseline_deadband_{c_occ - h_occ:.2f}_lt_{DEADBAND_PROTECTION_MIN}"
            skipped_zones.append(zname)
            continue
        # 정상 적용
        if h_occ is not None:
            z["htg_occupied_applied"] = h_occ + h_off
        if z.get("htg_setback") is not None:
            z["htg_setback_applied"] = z["htg_setback"] + h_off - sb
        if c_occ is not None:
            z["clg_occupied_applied"] = c_occ + c_off
        if z.get("clg_setback") is not None:
            z["clg_setback_applied"] = z["clg_setback"] + c_off + sb
        z["adjusted"] = True
        z["heating_offset"] = h_off
        z["cooling_offset"] = c_off
        z["setback_delta"]  = sb

    if skipped_zones:
        th["skipped_zones"] = skipped_zones


def _apply_hvac_availability(applied: dict, v: dict) -> None:
    """
    시간 단위 시프트: schedule.times_h에 shift를 더함 (mod 24, clip).
    실제 적용은 base-osm 코드에서 day schedule을 다시 작성할 때 사용.
    """
    shift = int(v["hvac_availability_shift"])
    av = applied["candidates"]["hvac_avail"]
    av["shift_h"] = shift
    for al in av.get("air_loops", []):
        s = al.get("summary", {})
        _shift_schedule_times(s, shift)
    # fan availability는 스케줄 객체로 이미 air_loops와 공유될 수 있음
    av["fans_shifted"] = shift


def _apply_envelope(applied: dict, v: dict) -> None:
    wall_m = v["wall_u_multiplier"]
    roof_m = v["roof_u_multiplier"]
    floor_m = v["floor_u_multiplier"]
    win_u_m  = v["window_u_multiplier"]
    win_g_m  = v["window_shgc_multiplier"]
    env = applied["candidates"]["envelope"]

    for cname, info in env.get("wall", {}).items():
        info["u_value_applied"] = _safe_mul(info.get("u_value_w_m2k"), wall_m)
        info["multiplier"] = wall_m
    for cname, info in env.get("roof", {}).items():
        info["u_value_applied"] = _safe_mul(info.get("u_value_w_m2k"), roof_m)
        info["multiplier"] = roof_m
    for cname, info in env.get("floor", {}).items():
        info["u_value_applied"] = _safe_mul(info.get("u_value_w_m2k"), floor_m)
        info["multiplier"] = floor_m
    for cname, info in env.get("window", {}).items():
        info["u_value_applied"] = _safe_mul(info.get("u_value_w_m2k"), win_u_m)
        info["shgc_applied"] = _safe_mul(info.get("shgc"), win_g_m)
        info["u_multiplier"] = win_u_m
        info["shgc_multiplier"] = win_g_m


def _apply_infiltration(applied: dict, v: dict) -> None:
    m = v["infiltration_multiplier"]
    inf = applied["candidates"]["infiltration"]
    for items in inf.get("by_space_or_type", {}).values():
        for r in items:
            for k in ("design_flow_rate", "flow_per_area", "flow_per_ext_area", "ach"):
                if r.get(k) is not None:
                    r[f"{k}_applied"] = r[k] * m
            r["multiplier"] = m


def _apply_ventilation(applied: dict, v: dict) -> None:
    m = v["oa_flow_multiplier"]
    vent = applied["candidates"]["ventilation"]
    for info in vent.get("by_dsoa", {}).values():
        for k in ("flow_per_person", "flow_per_area", "flow_per_zone", "ach"):
            if info.get(k) is not None:
                info[f"{k}_applied"] = info[k] * m
        info["multiplier"] = m


def _apply_dhw(applied: dict, v: dict) -> None:
    m = v["dhw_use_multiplier"]
    dhw = applied["candidates"]["dhw"]
    for defn in dhw.get("definitions", {}).values():
        if defn.get("peak_flow_m3_s") is not None:
            defn["peak_flow_applied"] = defn["peak_flow_m3_s"] * m
        defn["multiplier"] = m


def _apply_plant(applied: dict, v: dict) -> None:
    b_m = v["boiler_efficiency_multiplier"]
    c_m = v["chiller_cop_multiplier"]
    plant = applied["candidates"]["plant"]
    for b in plant.get("boilers", []):
        if b.get("efficiency") is not None:
            b["efficiency_applied"] = min(b["efficiency"] * b_m, 0.999)
        b["multiplier"] = b_m
    for ch in plant.get("chillers", []):
        if ch.get("cop") is not None:
            ch["cop_applied"] = ch["cop"] * c_m
        ch["multiplier"] = c_m
    for wh in plant.get("dhw_heaters", []):
        if wh.get("efficiency") is not None:
            wh["efficiency_applied"] = min(wh["efficiency"] * b_m, 0.999)
        wh["multiplier"] = b_m


def _apply_fans(applied: dict, v: dict) -> None:
    """
    fan_power_multiplier: 전력 P = (Q × ΔP) / η
        → ΔP에 곱하면 전력에 동등 효과 (효율 변경보다 안전)
    """
    m = v["fan_power_multiplier"]
    fans = applied["candidates"]["fans"]
    for f in fans.get("fans", []) + fans.get("exhaust_fans", []):
        if f.get("pressure_rise") is not None:
            f["pressure_rise_applied"] = f["pressure_rise"] * m
        f["multiplier"] = m


def _apply_thermal_mass(applied: dict, v: dict) -> None:
    m = v["thermal_mass_multiplier"]
    tm = applied["candidates"]["thermal_mass"]
    for im in tm.get("internal_masses", []):
        if im.get("surface_area_m2") is not None:
            im["surface_area_applied"] = im["surface_area_m2"] * m
        if im.get("area_per_floor") is not None:
            im["area_per_floor_applied"] = im["area_per_floor"] * m
        im["multiplier"] = m
    for z in tm.get("by_zone_surface_capacity", {}).values():
        if z.get("surface_thermal_capacity_kJ_K") is not None:
            z["surface_thermal_capacity_applied"] = z["surface_thermal_capacity_kJ_K"] * m
        z["multiplier"] = m


# ---------------------------------------------------------------------------
# Diagnostic / reality-agent 인터페이스
# ---------------------------------------------------------------------------
def compute_applied_summary(applied: dict) -> dict[str, Any]:
    """
    적용 후 값 요약. reality-agent가 trial 거부 여부를 판정할 때 참고.

    검출 항목 (building-agnostic, 일반 물리 범위만):
      - extreme_setpoint:   applied setpoint가 [12, 32] °C 범위를 벗어남
      - negative_value:     multiplier 적용 후 음수 (방어용)
      - efficiency_clipped: 보일러/DHW heater 효율이 0.999에 클립됨

    SpaceType별 비현실성(예: 클린룸 setpoint shift)은 reality-agent가
    baseline의 zone.space_type + applied 값을 보고 도메인 지식으로 판정한다.
    """
    th = applied["candidates"]["heating_setpoint_offset"]["targets"]
    plant_boilers = applied["candidates"]["boiler_efficiency_multiplier"]["targets"]
    plant_dhw = applied["candidates"]["dhw_use_multiplier"]["targets"]
    inf_targets = applied["candidates"]["infiltration_multiplier"]["targets"]

    extreme_setpoint = []
    for z in th:
        zname = z.get("zone")
        for k in ("htg_occupied_applied", "htg_setback_applied",
                 "clg_occupied_applied", "clg_setback_applied"):
            val = z.get(k)
            if val is not None and (val < 12.0 or val > 32.0):
                extreme_setpoint.append({"zone": zname, "field": k, "value": val})

    efficiency_clipped = []
    for b in plant_boilers:
        if b.get("efficiency_applied") == 0.999 or b.get("applied_value") == 0.999:
            efficiency_clipped.append({"name": b["name"], "kind": "boiler"})
    for wh in plant_dhw:
        if wh.get("efficiency_applied") == 0.999 or wh.get("applied_value") == 0.999:
            efficiency_clipped.append({"name": wh.get("definition_name"), "kind": "dhw"})

    negative_value = []
    for r in inf_targets:
        for k, val in r.items():
            if k.endswith("_applied") and val is not None and val < 0:
                negative_value.append({"infil": r.get("name"), "field": k, "value": val})

    return {
        "extreme_setpoint":      extreme_setpoint,
        "efficiency_clipped":    efficiency_clipped,
        "negative_value":        negative_value,
        "applied_vars":          applied.get("metadata", {}).get("applied_vars", {}),
    }


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def _safe_mul(x, m):
    return None if x is None else x * m


def _scale_schedule_summary(summary: dict, multiplier: float, cap_at_one: bool = False) -> None:
    """ScheduleRuleset/Constant 요약 dict의 values를 multiplier로 스케일."""
    if not isinstance(summary, dict):
        return
    if summary.get("type") == "constant" and summary.get("value") is not None:
        v = summary["value"] * multiplier
        summary["value_applied"] = min(v, 1.0) if cap_at_one else v
        summary["multiplier"] = multiplier
        return
    day = summary.get("default_day")
    if isinstance(day, dict) and day.get("values"):
        scaled = [val * multiplier for val in day["values"]]
        if cap_at_one:
            scaled = [min(val, 1.0) for val in scaled]
        day["values_applied"] = scaled
    for rule in summary.get("rules", []):
        rd = rule.get("day_schedule", {})
        if rd.get("values"):
            scaled = [val * multiplier for val in rd["values"]]
            if cap_at_one:
                scaled = [min(val, 1.0) for val in scaled]
            rd["values_applied"] = scaled
    summary["multiplier"] = multiplier


def _shift_schedule_times(summary: dict, shift_h: int) -> None:
    """스케줄 day의 times_h에 shift_h를 더함 (24h clip, 정렬)."""
    if not isinstance(summary, dict) or shift_h == 0:
        return
    def _shift(times, values):
        if not times:
            return times, values
        new = []
        for t, val in zip(times, values):
            nt = t + shift_h
            nt = max(0.0, min(24.0, nt))
            new.append((nt, val))
        new.sort(key=lambda x: x[0])
        return [t for t, _ in new], [v for _, v in new]

    day = summary.get("default_day")
    if isinstance(day, dict):
        nt, nv = _shift(day.get("times_h", []), day.get("values", []))
        day["times_h_applied"] = nt
        day["values_applied"] = nv
    for rule in summary.get("rules", []):
        rd = rule.get("day_schedule", {})
        nt, nv = _shift(rd.get("times_h", []), rd.get("values", []))
        rd["times_h_applied"] = nt
        rd["values_applied"] = nv


# ===========================================================================
# OSM Writer
#   조정된 변수(Optuna multiplier/offset)를 baseline OSM에 실제로 덮어쓴다.
#   - 카테고리별 _write_* 함수가 openstudio setter를 호출
#   - 모든 변수는 zone/SpaceType 무관 전역 적용
#   - 하나의 schedule이 여러 부하(People/Lights/Equipment)에 공유될 경우
#     People > Lights > Equipment 우선순위로 1번만 스케일됨
# ===========================================================================
def write_applied_to_osm(
    applied: dict[str, Any],
    baseline_osm_path: Path | str,
    out_osm_path: Path | str,
) -> dict[str, Any]:
    """baseline OSM 로드 → applied dict의 multiplier/offset을 setter로 덮어쓰기 → 저장.

    Args:
        applied:           apply_optuna_vars()의 반환 dict (metadata.applied_vars 포함).
        baseline_osm_path: 변형 전 baseline OSM 경로.
        out_osm_path:      변형된 trial OSM 저장 경로.

    Returns:
        쓰기 요약 dict (적용된 변수 + 객체 카운트).
    """
    v = applied.get("metadata", {}).get("applied_vars") or neutral_values()
    model = _load_model(Path(baseline_osm_path))

    counters: dict[str, int] = {}
    counters.update(_write_internal_loads(model, v))
    counters.update(_write_load_schedules(model, v))
    counters.update(_write_thermostat(model, v))
    counters.update(_write_hvac_availability(model, v))
    counters.update(_write_envelope(model, v, applied))
    counters.update(_write_infiltration(model, v))
    counters.update(_write_ventilation(model, v))
    counters.update(_write_dhw(model, v))
    counters.update(_write_plant(model, v))
    counters.update(_write_fans(model, v))
    counters.update(_write_thermal_mass(model, v))

    out_osm_path = Path(out_osm_path)
    out_osm_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(openstudio.path(str(out_osm_path)), True)

    return {
        "out_osm_path": str(out_osm_path),
        "applied_vars": v,
        "objects_modified": counters,
    }


# ---------------------------------------------------------------------------
# OSM setter helpers
# ---------------------------------------------------------------------------
def _write_internal_loads(model, v: dict) -> dict[str, int]:
    eq_m  = float(v["equipment_multiplier"])
    lt_m  = float(v["lighting_multiplier"])
    occ_m = float(v["occupancy_density_multiplier"])

    n_eq = 0
    for d in model.getElectricEquipmentDefinitions():
        old = _opt_value(d.wattsperSpaceFloorArea(), None)
        if old is not None:
            d.setWattsperSpaceFloorArea(old * eq_m); n_eq += 1
        old_pp = _opt_value(d.wattsperPerson(), None)
        if old_pp is not None:
            d.setWattsperPerson(old_pp * eq_m)

    n_lt = 0
    for d in model.getLightsDefinitions():
        old = _opt_value(d.wattsperSpaceFloorArea(), None)
        if old is not None:
            d.setWattsperSpaceFloorArea(old * lt_m); n_lt += 1
        old_pp = _opt_value(d.wattsperPerson(), None)
        if old_pp is not None:
            d.setWattsperPerson(old_pp * lt_m)

    n_occ = 0
    for d in model.getPeopleDefinitions():
        old = _opt_value(d.peopleperSpaceFloorArea(), None)
        if old is not None:
            d.setPeopleperSpaceFloorArea(old * occ_m); n_occ += 1
        old_n = _opt_value(d.numberofPeople(), None)
        if old_n is not None:
            d.setNumberofPeople(old_n * occ_m)

    return {"equipment_definitions": n_eq, "lights_definitions": n_lt, "people_definitions": n_occ}


def _write_load_schedules(model, v: dict) -> dict[str, int]:
    """People → Lights → Equipment 순으로 스케줄 스케일.
    공유 스케줄은 먼저 만나는 use case의 multiplier로만 1번 스케일됨."""
    occ_m   = float(v["occupancy_schedule_multiplier"])
    light_m = float(v["lighting_schedule_multiplier"])
    eq_m    = float(v["equipment_schedule_multiplier"])

    scaled: set = set()
    n_occ = n_lt = n_eq = 0

    for p in model.getPeoples():
        sch = _opt_get(p.numberofPeopleSchedule())
        if sch and _scale_schedule_in_place(sch, occ_m, scaled, cap_at_one=True):
            n_occ += 1

    for lt in model.getLightss():
        sch = _opt_get(lt.schedule())
        if sch and _scale_schedule_in_place(sch, light_m, scaled, cap_at_one=True):
            n_lt += 1

    for eq in model.getElectricEquipments():
        sch = _opt_get(eq.schedule())
        if sch and _scale_schedule_in_place(sch, eq_m, scaled, cap_at_one=True):
            n_eq += 1

    return {"occ_schedules": n_occ, "lighting_schedules": n_lt, "equipment_schedules": n_eq}


def _write_thermostat(model, v: dict) -> dict[str, int]:
    """Cleanroom-class 보호: thermostat의 heating max - cooling min < DEADBAND_PROTECTION_MIN
    이면 해당 thermostat의 스케줄은 modify 대상에서 제외 (offset 안 적용)."""
    h_off = float(v["heating_setpoint_offset"])
    c_off = float(v["cooling_setpoint_offset"])
    sb    = float(v["setback_delta_offset"])

    htg_handles: set = set()
    clg_handles: set = set()
    skipped_thermostats = 0
    for tstat in model.getThermostatSetpointDualSetpoints():
        h = _opt_get(tstat.heatingSetpointTemperatureSchedule())
        c = _opt_get(tstat.coolingSetpointTemperatureSchedule())
        # cleanroom-class 보호 (baseline deadband 임계 미만 thermostat 통째 skip)
        if h is not None and c is not None:
            _, h_max = _schedule_extremes(h)
            c_min, _ = _schedule_extremes(c)
            if (h_max is not None and c_min is not None
                    and (c_min - h_max) < DEADBAND_PROTECTION_MIN):
                skipped_thermostats += 1
                continue
        if h is not None: htg_handles.add(str(h.handle()))
        if c is not None: clg_handles.add(str(c.handle()))

    n_h = n_c = 0
    for sch in list(model.getScheduleRulesets()) + list(model.getScheduleConstants()):
        h = str(sch.handle())
        if h in htg_handles:
            _adjust_thermostat_schedule(sch, h_off, sb, kind="htg"); n_h += 1
        elif h in clg_handles:
            _adjust_thermostat_schedule(sch, c_off, sb, kind="clg"); n_c += 1

    return {
        "htg_schedules":        n_h,
        "clg_schedules":        n_c,
        "thermostats_skipped":  skipped_thermostats,
    }


def _write_hvac_availability(model, v: dict) -> dict[str, int]:
    shift = int(v["hvac_availability_shift"])
    if shift == 0:
        return {"hvac_avail_schedules": 0}

    handles: set = set()
    for al in model.getAirLoopHVACs():
        handles.add(str(al.availabilitySchedule().handle()))
    for getter in (
        lambda: model.getFanConstantVolumes(),
        lambda: model.getFanVariableVolumes(),
        lambda: model.getFanOnOffs(),
        lambda: model.getFanZoneExhausts(),
    ):
        try:
            for f in getter():
                sch = _opt_get(f.availabilitySchedule()) if hasattr(f, "availabilitySchedule") else None
                if sch is not None:
                    handles.add(str(sch.handle()))
        except Exception:
            continue

    n = 0
    for sch in list(model.getScheduleRulesets()):
        if str(sch.handle()) in handles:
            _shift_schedule_times_in_place(sch, shift); n += 1
    return {"hvac_avail_schedules": n}


def _write_envelope(model, v: dict, applied: dict) -> dict[str, int]:
    m_wall  = float(v["wall_u_multiplier"])
    m_roof  = float(v["roof_u_multiplier"])
    m_floor = float(v["floor_u_multiplier"])
    m_win_u = float(v["window_u_multiplier"])
    m_win_g = float(v["window_shgc_multiplier"])

    candidates = applied.get("candidates", {})
    wall_consts = {
        t.get("construction_name")
        for t in candidates.get("wall_u_multiplier", {}).get("targets", [])
        if t.get("construction_name")
    }
    roof_consts = {
        t.get("construction_name")
        for t in candidates.get("roof_u_multiplier", {}).get("targets", [])
        if t.get("construction_name")
    }
    floor_consts = {
        t.get("construction_name")
        for t in candidates.get("floor_u_multiplier", {}).get("targets", [])
        if t.get("construction_name")
    }

    scaled_layers: set = set()
    n_wall = n_roof = n_floor = 0
    for c in model.getConstructions():
        cname = _name_of(c)
        if cname in wall_consts:
            _scale_construction_u(c, m_wall, scaled_layers); n_wall += 1
        elif cname in roof_consts:
            _scale_construction_u(c, m_roof, scaled_layers); n_roof += 1
        elif cname in floor_consts:
            _scale_construction_u(c, m_floor, scaled_layers); n_floor += 1

    n_win = 0
    for sg in model.getSimpleGlazings():
        sg.setUFactor(sg.uFactor() * m_win_u)
        sg.setSolarHeatGainCoefficient(min(sg.solarHeatGainCoefficient() * m_win_g, 0.99))
        n_win += 1

    return {
        "wall_constructions":  n_wall,
        "roof_constructions":  n_roof,
        "floor_constructions": n_floor,
        "window_glazings":     n_win,
    }


def _write_infiltration(model, v: dict) -> dict[str, int]:
    m = float(v["infiltration_multiplier"])
    n = 0
    for inf in model.getSpaceInfiltrationDesignFlowRates():
        method = inf.designFlowRateCalculationMethod()
        if method == "Flow/Space":
            x = _opt_value(inf.designFlowRate(), None)
            if x is not None: inf.setDesignFlowRate(x * m); n += 1
        elif method == "Flow/Area":
            x = _opt_value(inf.flowperSpaceFloorArea(), None)
            if x is not None: inf.setFlowperSpaceFloorArea(x * m); n += 1
        elif method == "Flow/ExteriorArea":
            x = _opt_value(inf.flowperExteriorSurfaceArea(), None)
            if x is not None: inf.setFlowperExteriorSurfaceArea(x * m); n += 1
        elif method == "Flow/ExteriorWallArea":
            x = _opt_value(inf.flowperExteriorSurfaceArea(), None)
            if x is not None: inf.setFlowperExteriorSurfaceArea(x * m); n += 1
        elif method == "AirChanges/Hour":
            x = _opt_value(inf.airChangesperHour(), None)
            if x is not None: inf.setAirChangesperHour(x * m); n += 1
    return {"infiltration_objects": n}


def _write_ventilation(model, v: dict) -> dict[str, int]:
    m = float(v["oa_flow_multiplier"])
    n = 0
    for d in model.getDesignSpecificationOutdoorAirs():
        d.setOutdoorAirFlowperPerson(d.outdoorAirFlowperPerson() * m)
        d.setOutdoorAirFlowperFloorArea(d.outdoorAirFlowperFloorArea() * m)
        d.setOutdoorAirFlowRate(d.outdoorAirFlowRate() * m)
        d.setOutdoorAirFlowAirChangesperHour(d.outdoorAirFlowAirChangesperHour() * m)
        n += 1
    return {"dsoa_objects": n}


def _write_dhw(model, v: dict) -> dict[str, int]:
    m = float(v["dhw_use_multiplier"])
    n = 0
    for d in model.getWaterUseEquipmentDefinitions():
        d.setPeakFlowRate(d.peakFlowRate() * m); n += 1
    return {"dhw_definitions": n}


def _write_plant(model, v: dict) -> dict[str, int]:
    bm = float(v["boiler_efficiency_multiplier"])
    cm = float(v["chiller_cop_multiplier"])
    n_b = n_ch = n_wh = 0

    for b in model.getBoilerHotWaters():
        b.setNominalThermalEfficiency(min(b.nominalThermalEfficiency() * bm, 0.999)); n_b += 1

    for ch in model.getChillerElectricEIRs():
        if hasattr(ch, "setReferenceCOP") and hasattr(ch, "referenceCOP"):
            cop = ch.referenceCOP()
            if cop is not None:
                ch.setReferenceCOP(cop * cm); n_ch += 1

    for wh in model.getWaterHeaterMixeds():
        eff = _opt_value(wh.heaterThermalEfficiency(), None)
        if eff is not None:
            wh.setHeaterThermalEfficiency(min(eff * bm, 0.999)); n_wh += 1

    return {"boilers": n_b, "chillers": n_ch, "dhw_heaters": n_wh}


def _write_fans(model, v: dict) -> dict[str, int]:
    """팬 전력 P = (Q × ΔP) / η. ΔP에 곱해서 전력에 동등 효과."""
    m = float(v["fan_power_multiplier"])
    n = 0
    for getter in (
        model.getFanConstantVolumes,
        model.getFanVariableVolumes,
        model.getFanOnOffs,
        model.getFanZoneExhausts,
    ):
        try:
            for f in getter():
                if hasattr(f, "pressureRise") and hasattr(f, "setPressureRise"):
                    f.setPressureRise(f.pressureRise() * m); n += 1
        except Exception:
            continue
    return {"fans": n}


def _write_thermal_mass(model, v: dict) -> dict[str, int]:
    m = float(v["thermal_mass_multiplier"])
    n = 0
    if hasattr(model, "getInternalMassDefinitions"):
        try:
            for d in model.getInternalMassDefinitions():
                sa = _opt_value(d.surfaceArea(), None)
                if sa is not None:
                    d.setSurfaceArea(sa * m); n += 1
                sa_pf = _opt_value(d.surfaceAreaperSpaceFloorArea(), None)
                if sa_pf is not None:
                    d.setSurfaceAreaperSpaceFloorArea(sa_pf * m)
        except Exception:
            pass
    return {"internal_mass_definitions": n}


# ---------------------------------------------------------------------------
# Schedule / construction primitives
# ---------------------------------------------------------------------------
def _scale_schedule_in_place(schedule, multiplier: float, scaled: set, cap_at_one: bool) -> bool:
    """이미 스케일된 스케줄은 건너뜀. 처음 만나면 multiplier로 in-place 변경."""
    h = str(schedule.handle())
    if h in scaled:
        return False
    scaled.add(h)

    sc = schedule.to_ScheduleConstant()
    if sc.is_initialized():
        c = sc.get()
        new_v = c.value() * multiplier
        if cap_at_one: new_v = min(new_v, 1.0)
        c.setValue(new_v)
        return True

    sr = schedule.to_ScheduleRuleset()
    if sr.is_initialized():
        rs = sr.get()
        for day in [rs.defaultDaySchedule()] + [r.daySchedule() for r in rs.scheduleRules()]:
            _scale_day_schedule(day, multiplier, cap_at_one)
        return True
    return False


def _scale_day_schedule(day, multiplier: float, cap_at_one: bool) -> None:
    times = list(day.times())
    values = list(day.values())
    day.clearValues()
    for t, val in zip(times, values):
        new_v = val * multiplier
        if cap_at_one: new_v = min(new_v, 1.0)
        day.addValue(t, new_v)


def _schedule_extremes(schedule) -> tuple[float | None, float | None]:
    """스케줄 내 모든 day rule을 훑어 (min, max) 반환. 없으면 (None, None)."""
    sc = schedule.to_ScheduleConstant()
    if sc.is_initialized():
        v = sc.get().value()
        return (v, v)
    sr = schedule.to_ScheduleRuleset()
    if not sr.is_initialized():
        return (None, None)
    rs = sr.get()
    all_vals: list[float] = []
    for day in [rs.defaultDaySchedule()] + [r.daySchedule() for r in rs.scheduleRules()]:
        all_vals.extend(list(day.values()))
    if not all_vals:
        return (None, None)
    return (min(all_vals), max(all_vals))


def _adjust_thermostat_schedule(schedule, base_offset: float, setback_delta: float, kind: str) -> None:
    """온도 스케줄에 base_offset을 더하고, setback 분리값에 setback_delta 추가 적용.

    kind='htg': occupied=max, setback=min → setback에 -setback_delta
    kind='clg': occupied=min, setback=max → setback에 +setback_delta
    """
    sc = schedule.to_ScheduleConstant()
    if sc.is_initialized():
        c = sc.get()
        c.setValue(c.value() + base_offset)
        return

    sr = schedule.to_ScheduleRuleset()
    if not sr.is_initialized():
        return
    rs = sr.get()
    for day in [rs.defaultDaySchedule()] + [r.daySchedule() for r in rs.scheduleRules()]:
        times = list(day.times())
        values = list(day.values())
        if not values:
            continue
        v_max = max(values)
        v_min = min(values)
        has_setback = (v_max != v_min)
        day.clearValues()
        for t, val in zip(times, values):
            new_v = val + base_offset
            if has_setback:
                if kind == "htg" and val == v_min:
                    new_v -= setback_delta
                elif kind == "clg" and val == v_max:
                    new_v += setback_delta
            day.addValue(t, new_v)


def _shift_schedule_times_in_place(schedule, shift_h: int) -> None:
    sr = schedule.to_ScheduleRuleset()
    if not sr.is_initialized():
        return
    rs = sr.get()
    for day in [rs.defaultDaySchedule()] + [r.daySchedule() for r in rs.scheduleRules()]:
        times = list(day.times())
        values = list(day.values())
        if not times:
            continue
        new = []
        for t, val in zip(times, values):
            t_h = t.totalHours() + shift_h
            t_h = max(0.0, min(24.0, t_h))
            new.append((t_h, val))
        new.sort(key=lambda x: x[0])
        # 같은 시각 중복 제거 (마지막 값 우선)
        dedup: dict[float, float] = {}
        for t_h, val in new:
            dedup[t_h] = val
        day.clearValues()
        for t_h in sorted(dedup):
            hh = int(t_h)
            mm = int(round((t_h - hh) * 60))
            if hh == 24:
                hh, mm = 24, 0
            day.addValue(openstudio.Time(0, hh, mm, 0), dedup[t_h])


def _scale_construction_u(construction, multiplier: float, scaled_layers: set) -> None:
    """U_new = U_old × m. 각 layer의 R을 1/m배 (= conductivity ×m, thermalResistance /m).
    공유 layer는 1번만 스케일 (handle 기준)."""
    for layer in construction.layers():
        h = str(layer.handle())
        if h in scaled_layers:
            continue
        scaled_layers.add(h)
        som = layer.to_StandardOpaqueMaterial()
        if som.is_initialized():
            mat = som.get()
            mat.setConductivity(mat.conductivity() * multiplier)
            continue
        mom = layer.to_MasslessOpaqueMaterial()
        if mom.is_initialized():
            mat = mom.get()
            mat.setThermalResistance(mat.thermalResistance() / multiplier)
            continue
        ag = layer.to_AirGap()
        if ag.is_initialized():
            mat = ag.get()
            mat.setThermalResistance(mat.thermalResistance() / multiplier)
            continue


# ===========================================================================
# CLI
# ===========================================================================
if __name__ == "__main__":
    import argparse
    import json as _json
    from osm_calibration_params import load_params, save_params

    parser = argparse.ArgumentParser(description="Apply calibrated Optuna vars (dict + OSM modes)")
    parser.add_argument("baseline", help="Path to baseline params JSON")
    parser.add_argument("--vars",    help="Path to JSON dict of optuna vars (default: neutral)")
    parser.add_argument("--out",     help="Path to write applied dict JSON")
    parser.add_argument("--osm-in",  help="Path to baseline OSM (required for --osm-out)")
    parser.add_argument("--osm-out", help="Path to write modified trial OSM")
    args = parser.parse_args()

    bl = load_params(args.baseline)
    optuna_vars = None
    if args.vars:
        with open(args.vars, encoding="utf-8") as f:
            optuna_vars = _json.load(f)
    applied = apply_optuna_vars(bl, optuna_vars)
    summary = compute_applied_summary(applied)

    if args.out:
        save_params(applied, args.out)
        print(f"Wrote applied dict to {args.out}")

    if args.osm_out:
        if not args.osm_in:
            parser.error("--osm-out requires --osm-in")
        write_summary = write_applied_to_osm(applied, args.osm_in, args.osm_out)
        print(f"Wrote modified OSM to {args.osm_out}")
        print(f"Objects modified: {write_summary['objects_modified']}")

    print("Reality summary:", _json.dumps(summary, ensure_ascii=False, indent=2)[:400])
